"""FastAPI backend for the MovieCrew portal.

PLAN path (POST /api/plan): runs the full 7-agent pipeline and returns the
Project as JSON plus a session_id for follow-on storyboard calls.

STORYBOARD path (POST /api/storyboard / /approve / /regenerate): generates
one still image per shot for human review, then on approval promotes each
anchored shot's board image to its reference_image_ids.

TAKES path (GET /api/takes, GET /api/takes/.../video): lists the previz
clips Blender rendered per shot and serves them for review, so every take of
a shot can be compared side by side before one is chosen.

RENDER path (POST /api/render, GET /api/render/{job}): submits a chosen take
to a generative backend and polls it, downloading the finished clip into the
takes tree so the only copy does not live on a URL that expires.

RENDERS path (GET /api/renders, GET /api/renders/.../video): the other half
of the gallery — what came back from the model, grouped by shot beside the
takes that drove it, served locally and downloadable.

One key runs all three stages: $OPENROUTER_API_KEY covers the agents, the
storyboard stills, and the generative renders. Setting it switches the
defaults from mock to live; without it every stage stays offline and free.
$ANTHROPIC_API_KEY still drives the direct-to-Anthropic backend for anyone
who prefers it.

SETTINGS path (GET /api/settings, POST /api/settings): a local settings
screen for the same environment variables every section above reads via
os.environ — the OpenRouter key, the R2/S3 credentials, the public URLs.
POST is the one place in this file that deliberately accepts a secret in a
request body: the whole point is not re-exporting five values by hand every
time this process starts. What is saved lives in one file on the machine
running the portal (~/.moviecrew/settings.json by default), never in a
database or anywhere reachable from outside this process. GET never echoes
a secret's value back, only whether it is set and its last four characters.
See moviecrew.settings for the whitelist, the masking, and the precedence
between a real deployment env var and a value saved here.

Everywhere else, keys are read server-side from the process environment
only — no other request or response here ever carries one. The takes root
is likewise server-side config ($MOVIECREW_TAKES_ROOT): a browser cannot
point this process at an arbitrary directory outside what /api/settings
explicitly changes.
"""

from __future__ import annotations

import os
import re
import tempfile
import threading
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from ..agents import DETAIL_LEVELS, ContinuityAgent
from ..assets import (
    BUCKET_ENV,
    ENDPOINT_ENV,
    PUBLIC_BASE_ENV,
    AssetError,
    S3AssetStore,
    build_asset_store,
    is_reachable,
)
from ..crew import MovieCrew, run_continuity_check, write_checkpoint
from ..image import ImageProvider, MockImageProvider
from ..llm import LLMClient
from ..mock import MockLLMClient
from ..reference import FileReferenceImageProvider, ReferenceImageProvider
from ..studio import PlanProgress, Stage, StudioSession
from ..production import UnknownShot, resolve_shot
from ..render import FakeRenderClient, JobStatus, ShotSpec
from ..schema import Bible, ContinuityFlag, Project, RenderPlan
from ..settings import (
    SettingsError,
    apply_to_environ,
    apply_values,
    describe_settings,
    settings_path,
)
from ..takes import list_takes, resolve_video, save_take, shot_dir

# Fill in anything saved locally, but only where the real process
# environment does not already have it — a deployment that exported a key
# itself is never shadowed by a leftover local settings file. Called once,
# at import, so every env var read below (all of them lazy, none cached at
# import time) sees the merged result from the very first request.
apply_to_environ()

_BACKENDS = ("mock", "openrouter", "anthropic")
_STATIC_DIR = Path(__file__).parent / "static"

# Where Blender writes takes. Server-side only, deliberately: a request-supplied
# path would let any page this portal serves read arbitrary directories.
_TAKES_ROOT_ENV = "MOVIECREW_TAKES_ROOT"
_DEFAULT_TAKES_ROOT = "takes"

# A generative backend fetches the driving take over the internet, so it needs
# a URL it can actually reach — never this process's loopback address. Set to
# wherever this portal is publicly reachable (a tunnel, a LAN host, a deploy).
_PUBLIC_BASE_URL_ENV = "MOVIECREW_PUBLIC_BASE_URL"

_LOCAL_HOSTS = ("localhost", "127.0.0.1", "0.0.0.0", "[::1]", "::1")

_OPENROUTER_KEY_ENV = "OPENROUTER_API_KEY"
_DEFAULT_RENDER_MODEL = "bytedance/seedance-2.5"

# A provider's job id becomes a filename, so it is held to an id shape before
# it is ever joined to a path.
_JOB_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")

# Submitted renders, keyed by job id, so a browser can poll one.
_render_jobs: dict[str, dict] = {}

# Render clients are stateful and cache their model catalogue, so one is
# kept per key rather than rebuilt per request.
_render_clients: dict[str, object] = {}

# Asset stores, keyed by the configuration that produced them.
_asset_stores: dict[tuple, object] = {}

_DEFAULT_IMAGE_MODEL = "google/gemini-2.5-flash-image"

# In-memory session store keyed by session_id.
_sessions: dict[str, StudioSession] = {}

# Guards only the check-and-set of session.continuity_status to "running" —
# a few lines, not the continuity call itself, so one session's continuity
# check never blocks another's from starting. Sufficient for a single-
# process portal; not a substitute for a real job queue, which this app
# does not need.
_continuity_lock = threading.Lock()


# ---------------------------------------------------------------------- #
# Helpers                                                                 #
# ---------------------------------------------------------------------- #


def _build_llm(backend: str) -> LLMClient:
    if backend == "mock":
        return MockLLMClient()
    if backend == "openrouter":
        from ..llm_openrouter import OpenRouterLLMClient

        return OpenRouterLLMClient()
    if backend == "anthropic":
        from ..llm import AnthropicLLMClient

        return AnthropicLLMClient()
    raise ValueError(f"unknown backend: {backend!r} (must be one of {_BACKENDS})")


def _default_backend() -> str:
    """`openrouter` once a key is present, so the portal opens ready to run.

    Without one it stays on `mock`, which needs no key and no network — the
    portal must be useful before anyone has paid for anything.
    """
    return "openrouter" if os.environ.get(_OPENROUTER_KEY_ENV) else "mock"


def _build_image_provider() -> ImageProvider:
    """A real still generator when there's a key, the mock otherwise.

    Resolved per session rather than held at import, so setting the key and
    restarting is all it takes — and so the tests can swap it per test.
    """
    if not os.environ.get(_OPENROUTER_KEY_ENV):
        return MockImageProvider()
    try:
        from ..image_openrouter import OpenRouterImageProvider

        return OpenRouterImageProvider(model=_DEFAULT_IMAGE_MODEL)
    except Exception:
        # A storyboard that falls back to stubs is worth far more than a
        # plan endpoint that 502s: the shots and prompts are the payload.
        return MockImageProvider()


def _error(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": message})


def _session_or_error(session_id: str):
    session = _sessions.get(session_id)
    if session is None:
        return None, _error(404, f"session {session_id!r} not found")
    return session, None


def _apply_plan_progress(
    session: StudioSession, checkpoint_path: str, event: str, **data
) -> None:
    """Called from the background generation thread after each durable
    milestone crew.make() reports (see MovieCrew.make's on_progress).

    Ordering matters here, per the rule this whole feature exists to
    satisfy: the project is mutated first, then checkpointed to disk, and
    only *then* is session.plan_progress updated — the field GET
    .../plan's caller actually watches — so a poller can never observe a
    stage or count that outran what was actually retained.
    """
    with session.plan_lock:
        project = session.project
        if event == "scene_complete":
            project.scenes.append(data["scene"])
        elif event == "editor_complete":
            project.render_plan = RenderPlan(order=data["order"], chains=data["chains"])
        elif event == "prompt_complete":
            project.render_plan.intents.append(data["intent"])
        elif event == "plan_complete":
            # The authoritative Project crew.make() returns, replacing the
            # one built up incrementally above — same content, but now with
            # its final title/logline/bible/flags/est_duration_s exactly as
            # the ordinary (non-portal) pipeline would have produced them.
            session.project = project = data["project"]
            session.base_flags = list(project.render_plan.flags)

        write_checkpoint(project, checkpoint_path)

        progress = session.plan_progress
        if event == "director_complete":
            progress.stage = "writer"
        elif event == "writer_complete":
            progress.scene_count = data["scene_count"]
            progress.stage = "designer"
        elif event == "designer_complete":
            progress.stage = "cinematography"
        elif event == "scene_complete":
            progress.scenes_completed += 1
            if progress.scenes_completed >= progress.scene_count:
                # Every scene's shots are in; the editor call is next (it
                # runs once over every shot, not per scene), so this is the
                # one point where a distinct "editor" stage exists at all.
                progress.stage = "editor"
        elif event == "editor_complete":
            progress.shot_count = data["shot_count"]
            progress.stage = "prompting"
        elif event == "prompt_complete":
            progress.prompts_completed += 1
        elif event == "plan_complete":
            progress.stage = "complete"


def _run_plan_job(session: StudioSession, req: PlanRequest, checkpoint_path: str) -> None:
    """Runs crew.make() to completion on a background thread, publishing
    progress onto *session* as it goes.

    Started fire-and-forget from POST /api/plan, which has already
    returned by the time this runs — there is no caller left to raise an
    exception to, so a failure here is reported the same way progress
    normally is, through session.plan_progress, never raised.

    No Celery/Redis/database: a plain daemon thread updating this one
    session's own state, guarded by its own plan_lock, is the simplest
    mechanism that is still safe for a single-process portal.
    """
    with session.plan_lock:
        session.plan_progress.status = "running"

    def on_progress(event: str, **data) -> None:
        _apply_plan_progress(session, checkpoint_path, event, **data)

    try:
        llm = _build_llm(session.backend)
        reference_provider: Optional[ReferenceImageProvider] = (
            FileReferenceImageProvider(req.reference_dir) if req.reference_dir else None
        )
        crew = MovieCrew(llm, reference_provider=reference_provider, prompt_detail=req.detail)
        crew.make(
            req.concept,
            checkpoint_path=checkpoint_path,
            run_continuity=False,
            on_progress=on_progress,
        )
    except Exception as exc:
        with session.plan_lock:
            session.plan_progress.status = "failed"
            session.plan_progress.error = str(exc)
        return

    with session.plan_lock:
        session.plan_progress.status = "complete"


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


def _render_url(scene_id: str, shot_id: str, job_id: str) -> str:
    return f"/api/renders/{scene_id}/{shot_id}/{job_id}/video"


def _job_to_dict(job, context: Optional[dict] = None, *, local_path: Optional[str] = None) -> dict:
    context = context or {}
    # `video_url` points at the provider and is useless to a browser: an
    # OpenRouter result URL needs the API key as a bearer header, which a
    # <video> tag cannot send, and it expires besides. Once the render is on
    # disk the portal serves it itself, and that is what the player uses.
    render_url = (
        _render_url(context["scene_id"], context["shot_id"], job.job_id)
        if local_path and context.get("scene_id") and context.get("shot_id")
        else None
    )
    return {
        "job_id": job.job_id,
        "shot_id": job.shot_id,
        "status": job.status.value,
        "backend": job.backend,
        "model": job.model,
        "video_url": job.video_url,
        "render_url": render_url,
        "cost": job.cost,
        "error": job.error,
        "is_terminal": job.is_terminal,
        "take_id": context.get("take_id"),
        "local_path": local_path,
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


def render_path(root, scene_id: str, shot_id: str, job_id: str):
    """Where a generated render is kept: beside the take that drove it."""
    return shot_dir(root, scene_id, shot_id) / "renders" / f"{job_id}.mp4"


def _store_render(client, job, take):
    """Download a finished render into the takes tree, once.

    Returns the local path, or None if it could not be saved. A download
    failure is not fatal — the provider URL is still returned so the result
    is not lost from view.
    """
    destination = render_path(_takes_root(), take.scene_id, take.shot_id, job.job_id)
    if destination.is_file():
        return str(destination)
    try:
        saved = client.fetch(job, str(destination))
    except Exception:
        return None
    return saved


def _render_to_dict(path: Path, take) -> dict:
    job_id = path.stem
    try:
        stat = path.stat()
        size, mtime = stat.st_size, stat.st_mtime
    except OSError:
        size, mtime = 0, 0.0
    return {
        "job_id": job_id,
        "scene_id": take.scene_id,
        "shot_id": take.shot_id,
        "take_number": take.take_number,
        "take_id": take.take_id,
        "take_video_url": (
            f"/api/takes/{take.scene_id}/{take.shot_id}/{take.take_number}/video"
        ),
        "video_url": _render_url(take.scene_id, take.shot_id, job_id),
        "size_bytes": size,
        "created_at": (
            datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat() if mtime else ""
        ),
        "linked": job_id in take.renders,
    }


def _list_renders(root: Path, scene_id=None, shot_id=None) -> list[dict]:
    """Every generated render on disk, newest first, tied to its take.

    Driven by the files rather than by `take.renders`, for the same reason
    `next_take_number` scans files: a render that finished while the portal
    was restarting has no lineage recorded, and dropping it from the gallery
    would hide something that cost real money. The record still supplies the
    link, so an unlinked render is shown and flagged rather than lost.
    """
    out: list[dict] = []
    for take in list_takes(root, scene_id=scene_id, shot_id=shot_id):
        directory = shot_dir(root, take.scene_id, take.shot_id) / "renders"
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.mp4")):
            out.append(_render_to_dict(path, take))
    out.sort(key=lambda r: r["created_at"], reverse=True)
    return out


def _render_path_or_error(scene_id: str, shot_id: str, job_id: str):
    """Locate a stored render, refusing anything outside the takes root.

    `job_id` arrives from the URL, so it is checked against the id shape
    before it ever becomes a path segment, and the resolved file must still
    land inside the root. Both, not either: the pattern stops traversal and
    the containment check stops a symlink out.
    """
    if not _JOB_ID_RE.match(job_id):
        return None, _error(400, f"malformed job id: {job_id!r}")

    root = _takes_root()
    path = render_path(root, scene_id, shot_id, job_id)
    try:
        resolved = path.resolve()
        root_resolved = root.resolve()
    except OSError as exc:
        return None, _error(500, f"could not resolve render: {exc}")

    if not resolved.is_relative_to(root_resolved):
        return None, _error(403, "render resolves outside the takes root")
    if not resolved.is_file():
        return None, _error(404, f"no render {job_id} for {shot_id}")
    return resolved, None


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


def _public_base_url() -> str:
    return os.environ.get(_PUBLIC_BASE_URL_ENV, "").rstrip("/")


def _asset_store():
    """The configured asset store, cached.

    A store is stateless but resolving it re-reads the environment, and the
    S3 variant is the one a render depends on — building it per request would
    make a misconfiguration show up intermittently rather than at startup.
    """
    key = (
        os.environ.get(BUCKET_ENV, ""),
        os.environ.get(ENDPOINT_ENV, ""),
        os.environ.get(PUBLIC_BASE_ENV, ""),
        _public_base_url(),
    )
    cached = _asset_stores.get(key)
    if cached is None:
        cached = build_asset_store(
            local_root=str(_takes_root()), local_base_url=_public_base_url()
        )
        _asset_stores[key] = cached
    return cached


def _portal_take_url(take) -> Optional[str]:
    """The take's URL as served by this portal, if it is publicly addressable.

    The fallback for deployments with no bucket: a tunnel or a LAN address
    pointed at $MOVIECREW_PUBLIC_BASE_URL. A loopback address is refused —
    a provider resolving `127.0.0.1` reaches its own machine, not this one,
    and the render fails confusingly late.
    """
    base = _public_base_url()
    if not base or not is_reachable(base):
        return None
    return (
        f"{base}/api/takes/{take.scene_id}/{take.shot_id}/{take.take_number}/video"
    )


def _reference_url_for_take(take) -> tuple[Optional[str], Optional[str]]:
    """A URL a render backend can fetch this take from, uploading if needed.

    Prefers the asset store: with a bucket configured the take is uploaded
    once under a stable key and served from a CDN, which is durable and
    typed. Falls back to this portal's own address, which is what a tunnelled
    demo uses.

    Returns `(url, error)` rather than raising, because a failure here is
    configuration — the caller turns it into a 400 that says which knob is
    missing, not a traceback.
    """
    store = _asset_store()
    if store.serves_public_urls and isinstance(store, S3AssetStore):
        source = resolve_video(take, _takes_root())
        if not source.is_file():
            return None, f"take {take.take_id} has no video file to upload"
        key = f"takes/{take.scene_id}/{take.shot_id}/take_{take.take_number:03d}.mp4"
        existing = store.url(key)
        try:
            # Uploading is idempotent for our purposes: the same take always
            # lands on the same key, so a re-render costs one PUT, not a
            # duplicate object.
            asset = store.put(str(source), key)
        except AssetError as exc:
            return existing, f"could not upload take to the asset store: {exc}"
        return asset.url, None

    return _portal_take_url(take), None


def _render_client():
    """The configured render backend, or the offline fake.

    Defaults to the fake so nothing spends money by accident; a real backend
    is opted into by setting a key.

    Cached per key, because a client is stateful: a fresh instance per
    request could not poll a job it had submitted, and would re-fetch the
    model catalogue on every call.
    """
    key = os.environ.get(_OPENROUTER_KEY_ENV, "")
    cached = _render_clients.get(key)
    if cached is not None:
        return cached, None

    if not key:
        client = FakeRenderClient()
    else:
        try:
            from ..render_openrouter import OpenRouterRenderClient

            client = OpenRouterRenderClient()
        except Exception as exc:
            return None, f"could not start the render backend: {exc}"

    _render_clients[key] = client
    return client, None


def _spec_for(req, take, reference_video: Optional[str]):
    """Build the request spec from canonical project state where there is any.

    The order is deliberate: production state first, take second, explicit
    override last. A session id resolves the shot's intent and its *current*
    references — so a board approved a moment ago is in the request — and the
    take supplies only what it alone knows, the driving clip. Without a
    session the take's own metadata stands in, which is what makes a previz
    renderable before the pipeline has ever run.
    """
    session = _sessions.get(req.session_id) if req.session_id else None
    state = None
    if session is not None:
        try:
            state = resolve_shot(session.project, req.shot_id)
        except UnknownShot:
            return None, _error(
                404,
                f"session {req.session_id!r} has no shot {req.shot_id!r}; the take "
                "and the loaded project disagree.",
            )

    if state is not None:
        spec = ShotSpec.from_intent(
            state.intent,
            reference_images=state.reference_images,
            reference_video=reference_video,
        )
    elif req.prompt:
        spec = ShotSpec(
            shot_id=take.shot_id,
            prompt=req.prompt,
            duration_s=int(take.duration_s or 8),
            reference_video=reference_video,
        )
    else:
        return None, _error(
            400,
            "nothing to render: pass session_id so the shot's intent can be "
            "resolved from the project, or prompt to render the take directly.",
        )

    # Explicit overrides win, and only where they were actually given.
    if req.prompt and state is not None:
        spec.prompt = req.prompt
    if req.reference_images is not None:
        spec.reference_images = list(req.reference_images)
    if req.duration_s is not None:
        spec.duration_s = int(round(req.duration_s))
    return spec, None


def _find_take(scene_id: str, shot_id: str, take_number: int):
    root = _takes_root()
    return next(
        (
            t
            for t in list_takes(root, scene_id=scene_id, shot_id=shot_id)
            if t.take_number == take_number
        ),
        None,
    )


# ---------------------------------------------------------------------- #
# Request models                                                          #
# ---------------------------------------------------------------------- #


class PlanRequest(BaseModel):
    concept: str
    backend: str = ""
    detail: str = "cinematic"
    reference_dir: Optional[str] = None


class StoryboardRequest(BaseModel):
    session_id: str


class RenderRequest(BaseModel):
    """A request to generate one shot from one take.

    `session_id` is how the canonical project reaches this endpoint. With it,
    the shot's `ShotIntent` and its *current* reference images are resolved
    server-side and become the request — so approving a storyboard changes
    what the next render actually receives.

    `prompt` and `reference_images` are overrides, not the normal path. The
    browser reconstructing canonical filmmaking state and posting it back is
    exactly the arrangement that let an approved board and a submitted
    render disagree. They stay for the case where no plan is loaded at all —
    a take rendered straight from Blender — and are documented as such.
    """

    scene_id: str
    shot_id: str
    take_number: int
    session_id: Optional[str] = None
    prompt: str = ""
    model: str = ""
    reference_images: Optional[list[str]] = None
    duration_s: Optional[float] = None
    estimate_only: bool = False


class RegenerateRequest(BaseModel):
    session_id: str
    shot_id: str
    feedback: str = ""
    prompt: str | None = None


class SettingsUpdateRequest(BaseModel):
    """Only the fields being changed need to be present.

    A secret field absent here means "leave it as it is" — the browser
    never received its current value to send back unchanged, since
    /api/settings never echoes one. Send an empty string for a field to
    clear it instead.
    """

    values: dict[str, str]


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
        "default_backend": _default_backend(),
        "detail_levels": sorted(DETAIL_LEVELS),
        "takes_root": str(root),
        "takes_root_exists": root.is_dir(),
        "asset_store": _asset_store().name,
        "asset_store_public": _asset_store().serves_public_urls,
    }


@app.get("/api/settings")
def get_settings():
    """Every known setting's current state — never a secret's full value.

    See moviecrew.settings for the whitelist and the masking rule.
    """
    return {"fields": describe_settings(), "settings_path": str(settings_path())}


@app.post("/api/settings")
def update_settings(req: SettingsUpdateRequest):
    """Save the given values and apply them to this process immediately.

    No cache invalidation needed afterward: every place that reads one of
    these settings (_render_client, _asset_store, _build_llm, and friends)
    keys its own cache by the environment variable's current value, so a
    changed value is simply a cache miss next time it's read, not a stale
    hit.
    """
    try:
        apply_values(req.values)
    except SettingsError as exc:
        return _error(400, str(exc))
    return {"fields": describe_settings(), "settings_path": str(settings_path())}


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


@app.get("/api/renders")
def renders(scene_id: Optional[str] = None, shot_id: Optional[str] = None):
    """Every generated render on disk, grouped by shot.

    The other half of the takes gallery: takes are what you shot in Blender,
    renders are what came back from the model, and both are per-shot so a
    reviewer can put them side by side.
    """
    root = _takes_root()
    try:
        found = _list_renders(root, scene_id=scene_id, shot_id=shot_id)
    except OSError as exc:
        return _error(502, f"could not read takes root: {exc}")

    shots: dict[str, list[dict]] = {}
    for entry in found:
        shots.setdefault(entry["shot_id"], []).append(entry)

    return {
        "takes_root": str(root),
        "render_count": len(found),
        "shots": shots,
    }


@app.get("/api/renders/{scene_id}/{shot_id}/{job_id}/video")
def render_video(scene_id: str, shot_id: str, job_id: str, download: bool = False):
    path, err = _render_path_or_error(scene_id, shot_id, job_id)
    if err:
        return err
    headers = (
        {"Content-Disposition": f'attachment; filename="{shot_id}_{job_id}.mp4"'}
        if download
        else None
    )
    return FileResponse(path, media_type="video/mp4", headers=headers)


@app.get("/api/render/models")
def render_models():
    """Models the configured backend offers, and what each supports."""
    client, err = _render_client()
    if err:
        return _error(502, err)
    try:
        entries = client.models()
    except Exception as exc:
        return _error(502, f"could not list models: {exc}")

    return {
        "backend": client.name,
        "live": client.name != "fake",
        "default_model": _DEFAULT_RENDER_MODEL,
        "public_base_url": _public_base_url(),
        "models": entries,
    }


@app.post("/api/render")
def render_take(req: RenderRequest):
    """Generate a shot from a chosen take, which drives the camera motion."""
    take = _find_take(req.scene_id, req.shot_id, req.take_number)
    if take is None:
        return _error(404, f"take {req.shot_id}#{req.take_number} not found")

    client, err = _render_client()
    if err:
        return _error(502, err)

    model = req.model or _DEFAULT_RENDER_MODEL
    capabilities = client.capabilities(model)

    # The request is validated before the deployment is: a request naming a
    # shot this project does not have is wrong however the portal is hosted,
    # and saying so first gives the more useful error.
    reference_video, asset_warning = _reference_url_for_take(take)
    spec, err = _spec_for(req, take, reference_video)
    if err:
        return err

    if capabilities.supports_video_reference and reference_video is None:
        return _error(
            400,
            f"{model} drives motion from the take, but there is nowhere it can be "
            f"fetched from. Configure a bucket ({BUCKET_ENV}, {ENDPOINT_ENV}, "
            f"credentials and {PUBLIC_BASE_ENV}) or point {_PUBLIC_BASE_URL_ENV} at "
            f"a publicly reachable address for this portal. "
            + (asset_warning or "A provider cannot reach a loopback address."),
        )

    if req.estimate_only:
        return {
            "estimate_only": True,
            "model": model,
            "cost": client.estimate_cost(spec, model=model),
            "cost_unit": capabilities.cost_model.unit,
            "duration_s": capabilities.clamp_duration(spec.duration_s),
            "drives_motion_from_take": bool(
                capabilities.supports_video_reference and reference_video
            ),
        }

    try:
        job = client.submit(spec, model=model)
    except Exception as exc:
        return _error(502, f"render submission failed: {exc}")

    context = {
        "take_id": take.take_id,
        "scene_id": take.scene_id,
        "shot_id": take.shot_id,
        "take_number": take.take_number,
    }
    _render_jobs[job.job_id] = context
    return _job_to_dict(job, context)


@app.get("/api/render/{job_id}")
def render_status(job_id: str):
    client, err = _render_client()
    if err:
        return _error(502, err)
    try:
        job = client.poll(job_id)
    except Exception as exc:
        return _error(502, f"could not poll render: {exc}")

    # Download the finished render and record it against its take. A provider
    # URL is temporary, and this render cost real money — leaving it to expire
    # on someone else's server would lose the only copy.
    context = _render_jobs.get(job_id)
    local_path = None
    if context and job.status is JobStatus.SUCCEEDED:
        take = _find_take(context["scene_id"], context["shot_id"], context["take_number"])
        if take is not None:
            local_path = _store_render(client, job, take)
            if job_id not in take.renders:
                take.renders.append(job_id)
                try:
                    save_take(take, _takes_root())
                except OSError:
                    pass  # the render succeeded; lineage is best-effort

    return _job_to_dict(job, context, local_path=local_path)


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
    """Start plan generation and return immediately — see GET .../plan.

    Validates the request synchronously (no work has started yet, so a bad
    backend or detail level is still a fast 400), then mints the session
    and hands the actual pipeline run to a background thread. The session
    exists in _sessions, and this returns, before Director has even run:
    completed creative work must never stay trapped inside one long
    request, all the way from the first agent call, not just after it.
    """
    backend = req.backend or _default_backend()
    if backend not in _BACKENDS:
        return _error(400, f"unknown backend: {backend!r} (must be one of {_BACKENDS})")
    if req.detail not in DETAIL_LEVELS:
        return _error(
            400, f"unknown detail level: {req.detail!r} (must be one of {sorted(DETAIL_LEVELS)})"
        )

    session_id = str(uuid.uuid4())
    session_dir = str(Path(tempfile.gettempdir()) / "moviecrew-sessions" / session_id)
    checkpoint_path = str(Path(session_dir) / "project_checkpoint.json")

    # A placeholder, mutated in place as generation proceeds and replaced
    # outright by the real thing once plan_complete fires — see
    # _apply_plan_progress. Never returned to a caller as-is: GET .../plan
    # always reports plan_progress.status alongside it, so "" for a title
    # only ever appears together with status="queued"/"running".
    placeholder_project = Project(
        title="", logline="", bible=Bible(style="", palette="", mood="")
    )

    session = StudioSession(
        session_id=session_id,
        stage=Stage.SHOT_DEFS,
        project=placeholder_project,
        session_dir=session_dir,
        image_provider=_build_image_provider(),
        backend=backend,
        plan_progress=PlanProgress(),
    )
    _sessions[session_id] = session

    thread = threading.Thread(
        target=_run_plan_job, args=(session, req, checkpoint_path), daemon=True
    )
    thread.start()

    return {"session_id": session_id, "status": session.plan_progress.status}


@app.get("/api/session/{session_id}/plan")
def plan_status(session_id: str):
    """Current plan-generation progress, plus whatever generated data
    safely exists so far. Meant to be polled roughly once a second while
    status is "queued"/"running".

    The project's own fields (title, scenes, render_plan, ...) are merged
    in at the top level — the same shape /api/plan itself used to return
    before this PR — so the portal's existing plan renderer keeps working
    against this response unchanged; scenes and render_plan.intents simply
    grow between polls instead of arriving all at once.
    """
    session, err = _session_or_error(session_id)
    if err:
        return err

    with session.plan_lock:
        progress = session.plan_progress
        result = {
            "session_id": session_id,
            "status": progress.status,
            "stage": progress.stage,
            "scene_count": progress.scene_count,
            "scenes_completed": progress.scenes_completed,
            "shot_count": progress.shot_count,
            "prompts_completed": progress.prompts_completed,
            "error": progress.error,
            "continuity_status": session.continuity_status,
            **asdict(session.project),
        }
    return result


@app.post("/api/session/{session_id}/save")
def save_session(session_id: str):
    """Persist this session's current project to disk, on demand.

    The manual counterpart to crew.make()'s automatic pre-continuity
    checkpoint — same mechanism (Project.to_json() to a file in the
    session's own directory), triggered by a person instead of by the
    pipeline. Works regardless of whether continuity succeeded: a Project
    is complete and worth saving the moment crew.make() returns it: its
    render plan, every scene and shot, and every intent are already real
    generation, whether or not the continuity flags on it exist yet.
    """
    session, err = _session_or_error(session_id)
    if err:
        return err

    path = Path(session.session_dir) / "project.json"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(session.project.to_json(), encoding="utf-8")
    except OSError as exc:
        return _error(502, f"could not save project: {exc}")

    return {
        "session_id": session_id,
        "stage": session.stage.value,
        "saved_to": str(path),
        "continuity_status": session.continuity_status,
    }


@app.post("/api/session/{session_id}/continuity")
def run_session_continuity(session_id: str):
    """Run the continuity check against this session's existing Project.

    Analysis of what plan generation already produced, not a rerun of any
    part of producing it: only session.project's own scenes and
    render_plan.intents are read, and Director/Writer/Designer/
    Cinematographer/Editor/Prompter are never touched. Safe to call more
    than once — each call recombines a fresh continuity result with the
    session's fixed base_flags, so results from an earlier call are
    replaced, never accumulated alongside the new ones.

    Guarded against a second run starting while one is already in flight
    for this session (not against other sessions', which are independent):
    the check-and-set of continuity_status to "running" is the only part
    under _continuity_lock, so the lock is held only for that, never for
    the continuity call itself.

    Non-fatal by construction — run_continuity_check() never raises — so
    this always returns a normal 200 response; "failed" is a field in that
    response; it is not this endpoint's own success/failure.
    """
    session, err = _session_or_error(session_id)
    if err:
        return err

    if session.plan_progress.status != "complete":
        return _error(
            409,
            "plan generation has not finished yet "
            f"(status={session.plan_progress.status!r}); continuity analyzes a "
            "finished plan and cannot run until POST /api/plan's job completes.",
        )

    with _continuity_lock:
        if session.continuity_status == "running":
            return {
                "session_id": session_id,
                "continuity_status": "running",
                "message": "continuity is already running for this session",
                "flags": [asdict(f) for f in session.project.render_plan.flags],
            }
        session.continuity_status = "running"
        session.continuity_message = None

    # Building the client can fail the same way the continuity call itself
    # can (a missing key, a backend that cannot start) — treated the same
    # way here: a project-level warning and failed=True, never a raised
    # exception out of this endpoint.
    try:
        llm = _build_llm(session.backend)
    except Exception as exc:
        new_flags = [
            ContinuityFlag(
                target="project",
                kind="warning",
                message=(
                    f"Continuity check did not complete ({type(exc).__name__}: {exc}); "
                    "this plan has not been checked for cross-scene consistency."
                ),
            )
        ]
        failed = True
    else:
        continuity_agent = ContinuityAgent(llm)
        new_flags, failed = run_continuity_check(
            continuity_agent,
            session.project.scenes,
            session.project.render_plan.intents,
        )

    deduped: dict[tuple[str, str, str], ContinuityFlag] = {}
    for flag in session.base_flags + new_flags:
        deduped.setdefault((flag.kind, flag.target, flag.message), flag)
    session.project.render_plan.flags = list(deduped.values())

    session.continuity_status = "failed" if failed else "complete"
    session.continuity_message = new_flags[0].message if failed else None

    # Persist the outcome the same way the pre-continuity checkpoint was
    # written — same file, same format, now updated with continuity's
    # result (or the record of its failure) instead of missing it.
    write_checkpoint(
        session.project, str(Path(session.session_dir) / "project_checkpoint.json")
    )

    return {
        "session_id": session_id,
        "continuity_status": session.continuity_status,
        "message": session.continuity_message,
        "flags": [asdict(f) for f in session.project.render_plan.flags],
    }


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
        if req.prompt is not None and not req.prompt.strip():
            return _error(400, "Image prompt cannot be empty")
        session.revise(feedback=req.feedback, shot_id=req.shot_id, prompt=req.prompt)
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
