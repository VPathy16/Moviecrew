"""FastAPI backend for the MovieCrew portal.

PLAN path (POST /api/plan): runs the full 7-agent pipeline and returns the
Project as JSON plus a session_id for follow-on storyboard calls.

STORYBOARD path (POST /api/storyboard / /approve / /regenerate): generates
one still image per shot for human review, then on approval promotes each
anchored shot's board image to its reference_image_ids.

API keys (GEMINI_API_KEY / ANTHROPIC_API_KEY) are read server-side from the
process environment only — no request or response here ever carries one.
"""

from __future__ import annotations

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

_BACKENDS = ("mock", "anthropic")
_STATIC_DIR = Path(__file__).parent / "static"

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
    return {"ok": True, "backends": list(_BACKENDS), "detail_levels": sorted(DETAIL_LEVELS)}


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
