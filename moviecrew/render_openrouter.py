"""RenderClient backed by OpenRouter's video API.

One key, many models — the same shape `llm.AnthropicLLMClient` has, and the
reason this backend is worth having: the model becomes configuration rather
than a code change.

HTTP goes through `urllib` from the standard library rather than `requests`.
That is deliberate: MovieCrew's core has no third-party imports, which is
what lets the whole package drop into Blender's bundled Python with nothing
to install. A new dependency here would cost that.

The key is read from $OPENROUTER_API_KEY server-side and never travels in a
response. `transport` is injectable, which is how the tests exercise every
path with no network and no key.

Endpoints (https://openrouter.ai/docs):
  POST /api/v1/videos          submit, returns an id
  GET  /api/v1/videos/{id}     poll
  GET  /api/v1/videos/models   models and what each supports
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Callable, Optional

from .render import (
    CostModel,
    JobStatus,
    RenderCapabilities,
    RenderClient,
    RenderJob,
    ShotSpec,
)

API_ROOT = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "bytedance/seedance-2.5"
API_KEY_ENV = "OPENROUTER_API_KEY"

# Keys inside a catalogue entry's `pricing_skus`. The second one is how a
# model declares it accepts a driving video: there is no separate flag, but a
# model that prices video input takes video input.
VIDEO_SKU = "video_tokens"
VIDEO_INPUT_SKU = "video_tokens_with_video_input"

COST_UNIT_VIDEO_TOKEN = "usd_per_video_token"
COST_UNIT_CLIP = "usd"

# OpenRouter reports many status spellings; anything unrecognised is treated
# as still running rather than as success, so a caller never downloads a
# half-finished render.
_STATUS_MAP: dict[str, JobStatus] = {
    "queued": JobStatus.PENDING,
    "pending": JobStatus.PENDING,
    "starting": JobStatus.PENDING,
    "in_progress": JobStatus.RUNNING,
    "processing": JobStatus.RUNNING,
    "running": JobStatus.RUNNING,
    "succeeded": JobStatus.SUCCEEDED,
    "success": JobStatus.SUCCEEDED,
    "completed": JobStatus.SUCCEEDED,
    "complete": JobStatus.SUCCEEDED,
    "failed": JobStatus.FAILED,
    "error": JobStatus.FAILED,
    "cancelled": JobStatus.CANCELLED,
    "canceled": JobStatus.CANCELLED,
}


class RenderError(RuntimeError):
    """A backend call that could not be completed."""


def _urllib_transport(
    method: str, url: str, headers: dict[str, str], body: Optional[dict]
) -> dict[str, Any]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:400]
        raise RenderError(f"{method} {url} failed ({exc.code}): {detail}") from exc
    except urllib.error.URLError as exc:
        raise RenderError(f"{method} {url} unreachable: {exc.reason}") from exc


def _status_of(payload: dict[str, Any]) -> JobStatus:
    raw = str(payload.get("status", "")).lower()
    return _STATUS_MAP.get(raw, JobStatus.RUNNING)


def _video_url_of(payload: dict[str, Any]) -> Optional[str]:
    """Dig the output URL out of the shapes OpenRouter returns.

    A completed job returns its result under `unsigned_urls` — a list, and
    "unsigned" meaning the URL carries no credentials of its own, so fetching
    it needs the API key (see `fetch`). Confirmed against a live render;
    the other shapes are kept as fallbacks.
    """
    unsigned = payload.get("unsigned_urls")
    if isinstance(unsigned, list) and unsigned and isinstance(unsigned[0], str):
        return unsigned[0]

    for key in ("video_url", "url", "output_url"):
        if isinstance(payload.get(key), str):
            return payload[key]
    output = payload.get("output") or payload.get("video")
    if isinstance(output, str):
        return output
    if isinstance(output, dict):
        for key in ("url", "video_url"):
            if isinstance(output.get(key), str):
                return output[key]
    if isinstance(output, list) and output:
        first = output[0]
        if isinstance(first, str):
            return first
        if isinstance(first, dict):
            return first.get("url") or first.get("video_url")
    return None


def _cost_of(payload: dict[str, Any]) -> Optional[float]:
    usage = payload.get("usage")
    if isinstance(usage, dict):
        cost = usage.get("cost")
        if isinstance(cost, (int, float)):
            return float(cost)
    cost = payload.get("cost")
    return float(cost) if isinstance(cost, (int, float)) else None


class OpenRouterRenderClient(RenderClient):
    name = "openrouter"

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        api_root: str = API_ROOT,
        transport: Optional[Callable[..., dict[str, Any]]] = None,
        referer: str = "https://github.com/VPathy16/Moviecrew",
        title: str = "MovieCrew",
    ) -> None:
        self.model = model
        self.api_root = api_root.rstrip("/")
        self._transport = transport or _urllib_transport
        self._referer = referer
        self._title = title
        self._models_cache: Optional[list[dict[str, Any]]] = None

        # An injected transport is the test seam, and needs no key.
        self._api_key = api_key or os.environ.get(API_KEY_ENV, "")
        if not self._api_key and transport is None:
            raise RenderError(
                f"OpenRouterRenderClient needs an API key: set {API_KEY_ENV} in the "
                "environment, or pass api_key=... explicitly."
            )

    # ------------------------------------------------------------------ #
    # HTTP                                                                #
    # ------------------------------------------------------------------ #

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self._referer,
            "X-Title": self._title,
        }

    def _call(self, method: str, path: str, body: Optional[dict] = None) -> dict[str, Any]:
        return self._transport(method, f"{self.api_root}{path}", self._headers(), body)

    # ------------------------------------------------------------------ #
    # Models and capabilities                                             #
    # ------------------------------------------------------------------ #

    def models(self) -> list[dict[str, Any]]:
        if self._models_cache is None:
            payload = self._call("GET", "/videos/models")
            data = payload.get("data", payload.get("models", []))
            self._models_cache = data if isinstance(data, list) else []
        return self._models_cache

    def _model_entry(self, model: str) -> dict[str, Any]:
        for entry in self.models():
            if entry.get("id") == model:
                return entry
        return {}

    def capabilities(self, model: Optional[str] = None) -> RenderCapabilities:
        """Read a model's real limits from the catalogue.

        The field names here are the ones `/videos/models` actually returns —
        `supported_frame_images`, `pricing_skus` — not the plausible-looking
        names this once guessed at. Guessing was not a harmless slip: every
        lookup missed, so `supports_first_last_frame` was False for every
        model on the service, the cost model was always zero, and callers
        branching on capabilities could never reach the paths those models
        do support. The older names are still accepted so a differently
        shaped catalogue does not regress.

        Falls back to conservative values when the catalogue is unreachable
        or silent about a field — under-promising costs a shorter clip,
        over-promising costs a rejected request after the user has waited.
        """
        entry = self._model_entry(model or self.model)

        durations = entry.get("supported_durations") or entry.get("durations") or []
        numeric = [int(d) for d in durations if str(d).isdigit()]
        max_duration = max(numeric) if numeric else int(entry.get("max_duration_s") or 8)

        resolutions = tuple(
            str(r) for r in (entry.get("supported_resolutions") or entry.get("resolutions") or ())
        )
        ratios = tuple(
            str(r)
            for r in (entry.get("supported_aspect_ratios") or entry.get("aspect_ratios") or ())
        )

        skus = entry.get("pricing_skus") or {}

        # Nothing in the catalogue says "this model takes a video". The
        # billing SKUs do: a model priced for video input accepts video
        # input, and one that never bills for it does not.
        max_videos = int(entry.get("max_video_references") or 0)
        if not max_videos and (
            VIDEO_INPUT_SKU in skus or entry.get("supports_video_reference")
        ):
            max_videos = 1

        # `supported_frame_images` is a list of the positions a model accepts
        # (["first_frame", "last_frame"]), so its emptiness is the flag.
        frame_images = entry.get("supported_frame_images")
        if frame_images is None:
            frame_images = entry.get("supports_frame_images", entry.get("frame_images"))

        # The unit follows the source, because these are not the same thing:
        # a pricing SKU is per video token, the legacy field was per clip or
        # per second. Reporting one as the other would make an estimate wrong
        # by four orders of magnitude.
        pricing = entry.get("pricing") or {}
        legacy = pricing.get("video") or pricing.get("per_second")
        if skus.get(VIDEO_SKU):
            amount, unit = float(skus[VIDEO_SKU]), COST_UNIT_VIDEO_TOKEN
        elif legacy:
            amount, unit = float(legacy), COST_UNIT_CLIP
        else:
            amount, unit = 0.0, COST_UNIT_CLIP

        return RenderCapabilities(
            max_duration_s=max_duration,
            supported_resolutions=resolutions,
            supported_aspect_ratios=ratios,
            supports_first_last_frame=bool(frame_images),
            supports_video_reference=max_videos > 0,
            max_video_references=max_videos,
            max_image_references=int(entry.get("max_image_references") or 0),
            supports_audio=bool(entry.get("supports_audio", False)),
            cost_model=CostModel(unit=unit, amount=amount),
        )

    # ------------------------------------------------------------------ #
    # Submit / poll / fetch                                               #
    # ------------------------------------------------------------------ #

    def build_request(self, spec: ShotSpec, *, model: str) -> dict[str, Any]:
        """The request body for `spec`. Pure, so tests can assert on it.

        Reference media rides in `provider.options`, OpenRouter's pass-through
        to model-specific parameters — `video_urls` and `image_urls` are
        Seedance's own names, not OpenRouter's.
        """
        capabilities = self.capabilities(model)
        body: dict[str, Any] = {
            "model": model,
            "prompt": spec.prompt,
            "duration": capabilities.clamp_duration(spec.duration_s),
        }
        if spec.aspect_ratio:
            body["aspect_ratio"] = spec.aspect_ratio
        if spec.resolution:
            body["resolution"] = spec.resolution
        if spec.seed is not None:
            body["seed"] = spec.seed
        body["generate_audio"] = bool(spec.generate_audio)

        options: dict[str, Any] = {}
        if spec.reference_video and capabilities.supports_video_reference:
            options["video_urls"] = [spec.reference_video][
                : max(1, capabilities.max_video_references)
            ]
        if spec.reference_images:
            limit = capabilities.max_image_references or len(spec.reference_images)
            options["image_urls"] = list(spec.reference_images)[:limit]
        if spec.negative_prompt:
            options["negative_prompt"] = spec.negative_prompt
        if options:
            body["provider"] = {"options": options}

        return body

    def _job_from(self, payload: dict[str, Any], spec_shot_id: str, model: str) -> RenderJob:
        return RenderJob(
            job_id=str(payload.get("id") or payload.get("request_id") or ""),
            shot_id=spec_shot_id,
            status=_status_of(payload),
            backend=self.name,
            model=model,
            video_url=_video_url_of(payload),
            cost=_cost_of(payload),
            error=payload.get("error") if isinstance(payload.get("error"), str) else None,
            raw=payload,
        )

    def submit(self, spec: ShotSpec, *, model: str) -> RenderJob:
        body = self.build_request(spec, model=model)
        try:
            payload = self._call("POST", "/videos", body)
        except RenderError as exc:
            return RenderJob(
                job_id="",
                shot_id=spec.shot_id,
                status=JobStatus.FAILED,
                backend=self.name,
                model=model,
                error=str(exc),
            )
        return self._job_from(payload, spec.shot_id, model)

    def poll(self, job_id: str) -> RenderJob:
        try:
            payload = self._call("GET", f"/videos/{job_id}")
        except RenderError as exc:
            return RenderJob(
                job_id=job_id,
                shot_id="",
                status=JobStatus.FAILED,
                backend=self.name,
                error=str(exc),
            )
        job = self._job_from(payload, str(payload.get("shot_id") or ""), self.model)
        job.job_id = job.job_id or job_id
        return job

    def fetch(self, job: RenderJob, out_path: str) -> Optional[str]:
        if job.status is not JobStatus.SUCCEEDED or not job.video_url:
            return None
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

        # An OpenRouter result URL is unsigned: it sits behind the same API
        # auth as everything else, so a bare GET gets a 401. Sending the key
        # is harmless for a URL that does not need it.
        request = urllib.request.Request(job.video_url)
        if job.video_url.startswith(self.api_root) or "openrouter.ai" in job.video_url:
            request.add_header("Authorization", f"Bearer {self._api_key}")
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                data = response.read()
        except (urllib.error.URLError, OSError):
            return None
        with open(out_path, "wb") as handle:
            handle.write(data)
        return out_path
