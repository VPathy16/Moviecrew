"""FastAPI backend for the MovieCrew portal — the PLAN path only.

Builds a real MovieCrew over HTTP (mock or anthropic backend, any prompt
detail level) and returns the resulting Project as JSON. The long-running
render path (actual Veo calls) is a follow-up: it needs a job queue and the
live Veo smoke test first, so this app never touches moviecrew.video.

API keys (GEMINI_API_KEY / ANTHROPIC_API_KEY) are read from the server
process's environment only, by whichever LLMClient/VideoBackend reads them;
no request body or response here ever carries one.
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from ..agents import DETAIL_LEVELS
from ..crew import MovieCrew
from ..llm import LLMClient
from ..mock import MockLLMClient
from ..reference import FileReferenceImageProvider, ReferenceImageProvider

_BACKENDS = ("mock", "anthropic")
_STATIC_DIR = Path(__file__).parent / "static"


def _build_llm(backend: str) -> LLMClient:
    if backend == "mock":
        return MockLLMClient()
    if backend == "anthropic":
        from ..llm import AnthropicLLMClient

        return AnthropicLLMClient()
    raise ValueError(f"unknown backend: {backend!r} (must be one of {_BACKENDS})")


class PlanRequest(BaseModel):
    concept: str
    backend: str = "mock"
    detail: str = "cinematic"
    reference_dir: Optional[str] = None


def _error(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": message})


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

    return asdict(project)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(_STATIC_DIR / "index.html")
