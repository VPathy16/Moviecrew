"""FastAPI backend for the MovieCrew portal.

PLAN path (POST /api/plan): runs the full 7-agent pipeline and returns the
Project as JSON plus a session_id for follow-on storyboard calls.

STORYBOARD path (POST /api/storyboard / /approve / /regenerate): generates
one still image per shot for human review, then on approval promotes each
anchored shot's board image to its reference_image_ids.

TAKES path (GET /api/takes, GET /api/takes/.../video): lists the previz
clips Blender rendered per shot and serves them for review, so every take of
a shot can be compared side by side before one is chosen.

API keys (GEMINI_API_KEY / ANTHROPIC_API_KEY) are read server-side from the
process environment only — no request or response here ever carries one. The
takes root is likewise server-side config ($MOVIECREW_TAKES_ROOT): a browser
cannot point this process at an arbitrary directory.
"""

from __future__ import annotations

import os
import tempfile
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from ..agents import DETAIL_LEVELS
from ..crew import MovieCrew
from ..image import ImageProvider, MockImageProvider
from ..llm import LLMClient
from ..mock import MockLLMClient
from ..reference import FileReferenceImageProvider, ReferenceImageProvider
from ..studio import Stage, StudioSession
from ..takes import list_takes, resolve_video

_BACKENDS = ("mock", "anthropic")
_STATIC_DIR = Path(__file__).parent / "static"

# Where Blender writes takes. Server-side only, deliberately: a request-supplied
# path would let any page this portal serves read arbitrary directories.
_TAKES_ROOT_ENV = "MOVIECREW_TAKES_ROOT"
_DEFAULT_TAKES_ROOT = "takes"

# Module-level image provider: MockImageProvider for offline demos.
# Swap for a real provider (Imagen, SD, …) when one lands.
_image_provider: ImageProvider = MockImageProvider()

# In-memory session store keyed by session_id.
_sessions: dict[str, StudioSession] = {}


# ---------------------------------------------------------------------- #
# Helpers                                                                 #
# ---------------------------------------------------------------------- #


def _build_llm(backend: str) -> LLMClient:
    if backend == "mock":
        return MockLLMClient()
    if backend == "anthropic":
        from ..llm import AnthropicLLMClient

        return AnthropicLLMClient()
    raise ValueError(f"unknown backend: {backend!r} (must be one of {_BACKENDS})")


def _error(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": message})


def _session_or_error(session_id: str):
    session = _sessions.get(session_id)
    if session is None:
        return None, _error(404, f"session {session_id!r} not found")
    return session, None


def _frame_to_dict(session_id: str, frame) -> dict:
    return {
        "shot_id": frame.shot_id,
        "image_url": (
            f"/api/storyboard/{session_id}/{frame.shot_id}"
            if frame.image_path
            else None
        ),
        "prompt_used": frame.prompt_used,
        "status": frame.status,
    }


def _takes_root() -> Path:
    return Path(os.environ.get(_TAKES_ROOT_ENV, _DEFAULT_TAKES_ROOT)).expanduser()


def _take_to_dict(take, root: Path) -> dict:
    video = resolve_video(take, root)
    return {
        "take_id": take.take_id,
        "scene_id": take.scene_id,
        "shot_id": take.shot_id,
        "take_number": take.take_number,
        "video_url": (
            f"/api/takes/{take.scene_id}/{take.shot_id}/{take.take_number}/video"
        ),
        "has_video": video.is_file(),
        "duration_s": take.duration_s,
        "camera_move": take.camera_move,
        "lens": take.lens,
        "framing": take.framing,
        "resolution": take.resolution,
        "fps": take.fps,
        "blocked_by": take.blocked_by,
        "created_at": take.created_at,
        "media_id": take.media_id,
    }


def _video_path_or_error(scene_id: str, shot_id: str, take_number: int):
    """Locate a take's clip, refusing anything outside the takes root.

    The path is never assembled from the URL. The take is found among the
    records actually on disk, and the video it points at must still resolve
    inside the root — so neither a traversal in the URL nor a doctored
    `video_path` in a record can reach an unrelated file.
    """
    root = _takes_root()
    take = next(
        (
            t
            for t in list_takes(root, scene_id=scene_id, shot_id=shot_id)
            if t.take_number == take_number
        ),
        None,
    )
    if take is None:
        return None, _error(404, f"take {shot_id}#{take_number} not found")

    try:
        resolved = resolve_video(take, root).resolve()
        root_resolved = root.resolve()
    except OSError as exc:
        return None, _error(500, f"could not resolve take video: {exc}")

    if not resolved.is_relative_to(root_resolved):
        return None, _error(403, "take video resolves outside the takes root")
    if not resolved.is_file():
        return None, _error(404, f"take {take.take_id} has no video file yet")
    return resolved, None


# ---------------------------------------------------------------------- #
# Request models                                                          #
# ---------------------------------------------------------------------- #


class PlanRequest(BaseModel):
    concept: str
    backend: str = "mock"
    detail: str = "cinematic"
    reference_dir: Optional[str] = None


class StoryboardRequest(BaseModel):
    session_id: str


class RegenerateRequest(BaseModel):
    session_id: str
    shot_id: str
    feedback: str = ""


# ---------------------------------------------------------------------- #
# App                                                                     #
# ---------------------------------------------------------------------- #

app = FastAPI(title="MovieCrew Portal")
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    root = _takes_root()
    return {
        "ok": True,
        "backends": list(_BACKENDS),
        "detail_levels": sorted(DETAIL_LEVELS),
        "takes_root": str(root),
        "takes_root_exists": root.is_dir(),
    }


@app.get("/api/takes")
def takes(scene_id: Optional[str] = None, shot_id: Optional[str] = None):
    """Every take under the takes root, grouped by shot.

    Grouped rather than flat because the gallery's unit is a shot: its takes
    are what a reviewer compares against each other.
    """
    root = _takes_root()
    try:
        found = list_takes(root, scene_id=scene_id, shot_id=shot_id)
    except OSError as exc:
        return _error(502, f"could not read takes root: {exc}")

    shots: dict[str, list[dict]] = {}
    for take in found:
        shots.setdefault(take.shot_id, []).append(_take_to_dict(take, root))

    return {
        "takes_root": str(root),
        "takes_root_exists": root.is_dir(),
        "take_count": len(found),
        "shots": shots,
    }


@app.get("/api/takes/{scene_id}/{shot_id}/{take_number}/video")
def take_video(scene_id: str, shot_id: str, take_number: int):
    path, err = _video_path_or_error(scene_id, shot_id, take_number)
    if err:
        return err
    # FileResponse honours Range requests, so the player can seek without
    # pulling the whole clip.
    return FileResponse(path, media_type="video/mp4")


@app.post("/api/plan")
def plan(req: PlanRequest):
    if req.backend not in _BACKENDS:
        return _error(400, f"unknown backend: {req.backend!r} (must be one of {_BACKENDS})")
    if req.detail not in DETAIL_LEVELS:
        return _error(
            400, f"unknown detail level: {req.detail!r} (must be one of {sorted(DETAIL_LEVELS)})"
        )

    try:
        llm = _build_llm(req.backend)
    except Exception as exc:
        return _error(502, f"could not start the {req.backend} backend: {exc}")

    reference_provider: Optional[ReferenceImageProvider] = (
        FileReferenceImageProvider(req.reference_dir) if req.reference_dir else None
    )

    try:
        crew = MovieCrew(llm, reference_provider=reference_provider, prompt_detail=req.detail)
        project = crew.make(req.concept)
    except Exception as exc:
        return _error(502, f"plan generation failed: {exc}")

    session_id = str(uuid.uuid4())
    session_dir = str(
        Path(tempfile.gettempdir()) / "moviecrew-sessions" / session_id
    )
    session = StudioSession(
        session_id=session_id,
        stage=Stage.SHOT_DEFS,
        project=project,
        session_dir=session_dir,
        image_provider=_image_provider,
    )
    _sessions[session_id] = session

    result = asdict(project)
    result["session_id"] = session_id
    result["stage"] = session.stage.value
    return result


@app.post("/api/storyboard")
def storyboard(req: StoryboardRequest):
    session, err = _session_or_error(req.session_id)
    if err:
        return err
    try:
        session.produce()
    except Exception as exc:
        return _error(502, f"storyboard generation failed: {exc}")
    return {
        "session_id": req.session_id,
        "stage": session.stage.value,
        "frames": [_frame_to_dict(req.session_id, f) for f in session.board],
    }


@app.post("/api/storyboard/approve")
def approve_storyboard(req: StoryboardRequest):
    session, err = _session_or_error(req.session_id)
    if err:
        return err
    if session.stage not in (Stage.STORYBOARD, Stage.OUTPUT):
        return _error(400, f"cannot approve from stage {session.stage.value!r}")
    try:
        session.approve()
    except Exception as exc:
        return _error(502, f"approve failed: {exc}")
    return {"session_id": req.session_id, "stage": session.stage.value}


@app.post("/api/storyboard/regenerate")
def regenerate_storyboard(req: RegenerateRequest):
    session, err = _session_or_error(req.session_id)
    if err:
        return err
    try:
        session.revise(feedback=req.feedback, shot_id=req.shot_id)
    except Exception as exc:
        return _error(502, f"regeneration failed: {exc}")
    frame = next((f for f in session.board if f.shot_id == req.shot_id), None)
    if frame is None:
        return _error(404, f"shot {req.shot_id!r} not found in board")
    return {
        "session_id": req.session_id,
        "stage": session.stage.value,
        "frame": _frame_to_dict(req.session_id, frame),
    }


@app.get("/api/storyboard/{session_id}/{shot_id}")
def storyboard_image(session_id: str, shot_id: str):
    session = _sessions.get(session_id)
    if session is None:
        return _error(404, f"session {session_id!r} not found")
    frame = next((f for f in session.board if f.shot_id == shot_id), None)
    if frame is None or frame.image_path is None:
        return _error(404, f"no image for shot {shot_id!r}")
    return FileResponse(frame.image_path, media_type="image/png")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(_STATIC_DIR / "index.html")
