"""Model-agnostic video-render abstraction.

Mirrors `llm.LLMClient`: one interface the pipeline talks to, with backends
behind it and the SDK-or-network dependency imported lazily so this module
always imports. `FakeRenderClient` is the offline default, so the whole
generate path can be exercised without spending credits.

Rendering is asynchronous everywhere, so the interface is submit / poll /
fetch rather than a single blocking call.

`capabilities()` is what callers branch on — never the backend's name. Models
differ on clip length, resolution, and crucially on whether they accept a
*video* as a reference. A previz take can drive camera motion on a backend
that takes video references; on one that doesn't, the take contributes its
first and last frame as keyframes instead (see `moviecrew.frames`). That
choice belongs to a capability check, not an `if backend == ...`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Sequence


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"

    @property
    def is_terminal(self) -> bool:
        return self in (JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED)


@dataclass(frozen=True)
class CostModel:
    """What a backend charges, and in what unit."""

    unit: str  # "usd" | "usd_per_second" | "credits_per_clip"
    amount: float = 0.0
    currency: str = "USD"


@dataclass(frozen=True)
class RenderCapabilities:
    """What a backend can actually do. Branch on this, not on `name`."""

    max_duration_s: int
    supported_resolutions: tuple[str, ...] = ()
    supported_aspect_ratios: tuple[str, ...] = ()
    supports_first_last_frame: bool = False
    supports_video_reference: bool = False
    max_video_references: int = 0
    max_image_references: int = 0
    supports_audio: bool = False
    cost_model: CostModel = CostModel(unit="usd")

    def clamp_duration(self, seconds: float) -> int:
        """The nearest duration this backend will actually accept."""
        return max(1, min(int(round(seconds)), self.max_duration_s))


@dataclass
class ShotSpec:
    """One render request, in backend-neutral terms.

    The execution-side twin of `schema.ShotIntent`: an intent says what the
    shot should be, a spec says what this request will carry. They are kept
    apart because a spec holds things no intent should know — a resolution,
    a seed, a URL a provider can fetch a driving take from. `from_intent` is
    the one-way adapter.

    `reference_video` is the previz take driving camera motion;
    `first_frame` / `last_frame` are its bookend stills, used by backends
    that cannot take a video.
    """

    shot_id: str
    prompt: str
    negative_prompt: str = ""
    duration_s: int = 8
    aspect_ratio: str = "16:9"
    resolution: str = "720p"
    reference_video: Optional[str] = None
    reference_images: list[str] = field(default_factory=list)
    first_frame: Optional[str] = None
    last_frame: Optional[str] = None
    generate_audio: bool = False
    seed: Optional[int] = None

    @classmethod
    def from_intent(
        cls,
        intent: Any,
        *,
        reference_images: Sequence[str] = (),
        **overrides: Any,
    ) -> "ShotSpec":
        """Adapt a `ShotIntent` into a request spec.

        References are passed in rather than read off the intent: they live
        on the `Shot`, which storyboard approval mutates, so they are
        resolved from live project state at execution time
        (`production.resolve_shot`) instead of copied at plan time and left
        to go stale.

        Duration is rounded to whole seconds here and clamped later by the
        backend's own `capabilities.clamp_duration`, so the intent keeps the
        length that was actually wanted.
        """
        spec = cls(
            shot_id=intent.shot_id,
            prompt=intent.description,
            negative_prompt=getattr(intent, "negative", ""),
            duration_s=int(round(getattr(intent, "duration_s", 8))),
            aspect_ratio=getattr(intent, "aspect_ratio", "16:9"),
            reference_images=list(reference_images),
        )
        for key, value in overrides.items():
            setattr(spec, key, value)
        return spec


@dataclass
class RenderJob:
    """A submitted render, and what became of it.

    `poll()` returns this rather than a bare status: a status alone cannot
    carry the cost actually charged or the reason a render failed, and both
    need recording against the take.
    """

    job_id: str
    shot_id: str
    status: JobStatus
    backend: str = ""
    model: str = ""
    video_url: Optional[str] = None
    cost: Optional[float] = None
    error: Optional[str] = None
    raw: Optional[dict[str, Any]] = None

    @property
    def is_terminal(self) -> bool:
        return self.status.is_terminal


class RenderClient(ABC):
    """The seam between the pipeline and a video-generation backend."""

    name: str = ""

    @abstractmethod
    def capabilities(self, model: Optional[str] = None) -> RenderCapabilities:
        """What this backend (optionally, this model) supports."""
        raise NotImplementedError

    @abstractmethod
    def models(self) -> list[dict[str, Any]]:
        """Models this backend offers, newest-first where it says so."""
        raise NotImplementedError

    @abstractmethod
    def submit(self, spec: ShotSpec, *, model: str) -> RenderJob:
        """Start a render. Returns immediately with a job to poll."""
        raise NotImplementedError

    @abstractmethod
    def poll(self, job_id: str) -> RenderJob:
        """Current state of a submitted render."""
        raise NotImplementedError

    @abstractmethod
    def fetch(self, job: RenderJob, out_path: str) -> Optional[str]:
        """Download a finished render. Returns the local path, or None."""
        raise NotImplementedError

    def estimate_cost(self, spec: ShotSpec, *, model: str) -> Optional[float]:
        """Cost of `spec` without submitting it, when the backend can say.

        None means "unknown", which a caller must surface as unknown rather
        than as free — these renders bill real money.
        """
        return None


class FakeRenderClient(RenderClient):
    """In-memory backend for tests and offline demos. Spends nothing.

    Succeeds immediately by default. `fail_with` makes every submission fail,
    and `pending_polls` holds jobs RUNNING for a number of polls first, so
    callers' waiting logic can be exercised deterministically.
    """

    name = "fake"

    def __init__(
        self,
        *,
        capabilities: Optional[RenderCapabilities] = None,
        fail_with: Optional[str] = None,
        pending_polls: int = 0,
        cost: float = 0.0,
    ) -> None:
        self._capabilities = capabilities or RenderCapabilities(
            max_duration_s=30,
            supported_resolutions=("480p", "720p"),
            supported_aspect_ratios=("16:9", "9:16"),
            supports_first_last_frame=True,
            supports_video_reference=True,
            max_video_references=3,
            max_image_references=9,
            cost_model=CostModel(unit="usd", amount=cost),
        )
        self._fail_with = fail_with
        self._pending_polls = pending_polls
        self._cost = cost
        self.submitted: list[tuple[ShotSpec, str]] = []
        self._jobs: dict[str, RenderJob] = {}
        self._remaining: dict[str, int] = {}
        self._counter = 0

    def capabilities(self, model: Optional[str] = None) -> RenderCapabilities:
        return self._capabilities

    def models(self) -> list[dict[str, Any]]:
        return [{"id": "fake/model", "name": "Fake Model", "max_duration_s": 30}]

    def submit(self, spec: ShotSpec, *, model: str) -> RenderJob:
        self._counter += 1
        job_id = f"fake-{self._counter:04d}"
        self.submitted.append((spec, model))

        if self._fail_with:
            job = RenderJob(
                job_id=job_id,
                shot_id=spec.shot_id,
                status=JobStatus.FAILED,
                backend=self.name,
                model=model,
                error=self._fail_with,
            )
        else:
            job = RenderJob(
                job_id=job_id,
                shot_id=spec.shot_id,
                status=JobStatus.RUNNING if self._pending_polls else JobStatus.SUCCEEDED,
                backend=self.name,
                model=model,
                video_url=None if self._pending_polls else f"fake://{job_id}.mp4",
                cost=None if self._pending_polls else self._cost,
            )
            self._remaining[job_id] = self._pending_polls

        self._jobs[job_id] = job
        return job

    def poll(self, job_id: str) -> RenderJob:
        job = self._jobs.get(job_id)
        if job is None:
            return RenderJob(
                job_id=job_id,
                shot_id="",
                status=JobStatus.FAILED,
                backend=self.name,
                error=f"unknown job {job_id!r}",
            )
        left = self._remaining.get(job_id, 0)
        if left > 0:
            self._remaining[job_id] = left - 1
            if left - 1 == 0:
                job.status = JobStatus.SUCCEEDED
                job.video_url = f"fake://{job_id}.mp4"
                job.cost = self._cost
        return job

    def fetch(self, job: RenderJob, out_path: str) -> Optional[str]:
        if job.status is not JobStatus.SUCCEEDED:
            return None
        import os

        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "wb") as handle:
            handle.write(b"\x00\x00\x00\x18ftypisom")  # a stand-in MP4 header
        return out_path

    def estimate_cost(self, spec: ShotSpec, *, model: str) -> Optional[float]:
        return self._cost
