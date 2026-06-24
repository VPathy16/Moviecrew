"""Video rendering backends: turn a VeoPrompt into a rendered (or stubbed) clip.

VideoBackend is the seam between the orchestrator and an actual video API.
StubVideoBackend never touches the network: it only builds and records the
request payload a real backend would send, so the pipeline stays fully
testable offline. VeoBackend will talk to the real Veo API once the
`google-genai` SDK and credentials are available; it imports the SDK
lazily so this module always imports cleanly without it installed.
"""

from __future__ import annotations

import mimetypes
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

from .schema import VEO_MAX_DURATION_S, VEO_MAX_REFERENCE_IMAGES, VeoPrompt

# See https://ai.google.dev/gemini-api/docs/video for the current Veo model
# catalog; pin a default here so callers don't have to know the exact id.
DEFAULT_VEO_MODEL = "veo-3.1-generate-preview"

# Veo 3.1 defaults to 720p; 1080p/4k (like reference-conditioned generation)
# are only available for 8s clips, per
# https://ai.google.dev/gemini-api/docs/video.
DEFAULT_VEO_RESOLUTION = "720p"
_VEO_HIGH_RESOLUTIONS = {"1080p", "4k"}


@dataclass
class RenderResult:
    shot_id: str
    status: str  # "stubbed" | "succeeded" | "failed" | ...
    backend: str
    uri: Optional[str] = None
    raw: Optional[dict[str, Any]] = None


def build_request(
    prompt: VeoPrompt,
    *,
    model: str = DEFAULT_VEO_MODEL,
    extend_from: Optional[str] = None,
    in_multishot_chain: bool = False,
) -> dict[str, Any]:
    """The backend-agnostic request payload every VideoBackend builds from a
    VeoPrompt. `extend_from` is the shot id of the clip this one continues
    from (Veo's extend-final-frame feature); None for a chain's first shot
    or a standalone shot. `in_multishot_chain` flags a shot that belongs to
    a chain of 2+ shots (its head or one of its extensions).
    """
    return {
        "model": model,
        "prompt": prompt.prompt,
        "negative_prompt": prompt.negative_prompt,
        "duration_s": prompt.duration_s,
        "aspect_ratio": prompt.aspect_ratio,
        "reference_images": list(prompt.reference_images),
        "extend_from": extend_from,
        "in_multishot_chain": in_multishot_chain,
    }


class VideoBackend(ABC):
    """Renders one VeoPrompt into a clip (or a stand-in result)."""

    name: str = ""

    @abstractmethod
    def render(
        self,
        prompt: VeoPrompt,
        *,
        extend_from: Optional[str] = None,
        in_multishot_chain: bool = False,
    ) -> RenderResult:
        raise NotImplementedError


class StubVideoBackend(VideoBackend):
    """Offline backend: builds the request a real backend would send and
    returns it unsent, so the pipeline can be exercised with no network
    access and no API key.
    """

    name = "stub"

    def __init__(self, model: str = DEFAULT_VEO_MODEL) -> None:
        self.model = model

    def render(
        self,
        prompt: VeoPrompt,
        *,
        extend_from: Optional[str] = None,
        in_multishot_chain: bool = False,
    ) -> RenderResult:
        request = build_request(
            prompt, model=self.model, extend_from=extend_from, in_multishot_chain=in_multishot_chain
        )
        return RenderResult(
            shot_id=prompt.shot_id,
            status="stubbed",
            backend=self.name,
            uri=None,
            raw=request,
        )


class VeoBackend(VideoBackend):
    """Renders standalone clips via the real Veo 3.1 API (google-genai SDK).

    The SDK is imported lazily inside __init__ so this module always
    imports cleanly without it installed; instantiating without the SDK
    or an API key raises a clear error naming exactly what's missing.
    Passing `client=` (a pre-built google.genai.Client, or any object
    exposing the same `.models.generate_videos` / `.operations.get` /
    `.files.download` surface) skips the import and key check entirely —
    that's the seam tests use to run this fully offline.

    Confirmed against the installed google-genai SDK (2.x) and
    https://ai.google.dev/gemini-api/docs/video:
      - `generate_videos(model=, prompt=, image=, config=)` returns a
        GenerateVideosOperation; poll via `client.operations.get(operation)`
        until `.done`, then `.response.generated_videos[0]`.
      - `GenerateVideosConfig` accepts `aspect_ratio`, `resolution`,
        `duration_seconds` (an int — not a string), `reference_images`
        (up to 3, each `{"image": ImageDict, "reference_type": "asset"}`),
        and `negative_prompt`.
      - 1080p/4k and reference-image-conditioned generation are only
        available for 8s clips; this backend coerces duration to 8s
        rather than send an illegal combination.

    `config` and `reference_images` are built as plain dicts (the SDK's
    documented `*Dict` shapes) rather than `google.genai.types.*` model
    instances, so render() never needs the SDK import even on the real
    path — keeping the request-building logic identical for both real and
    injected-client use.

    Extending a clip (`extend_from` set) continues a previous shot's Veo
    generation via `generate_videos(model=, prompt=, video=<predecessor's
    Video>, config={"number_of_videos": 1, "resolution": "720p"})` — no
    `image`, `duration_seconds`, or `reference_images` on that call, and
    only 720p is supported for extension (confirmed against the installed
    google-genai SDK and https://ai.google.dev/gemini-api/docs/video).
    Extension output is cumulative (predecessor + ~7s), so the last shot
    of a chain is the whole continuous take. One VeoBackend instance is
    meant to render one film: `produced_video_by_shot_id` caches the SDK's
    own Video object from every successful render (standalone or
    extension) so the next extension in a chain can pass it straight back
    in, with no SDK import required to do so.
    """

    name = "veo"

    def __init__(
        self,
        model: str = DEFAULT_VEO_MODEL,
        *,
        api_key: Optional[str] = None,
        client: Optional[Any] = None,
        out_dir: str = "renders",
        poll_interval_s: float = 10,
        timeout_s: float = 600,
        resolution: str = DEFAULT_VEO_RESOLUTION,
    ) -> None:
        self.model = model
        self.out_dir = out_dir
        self.poll_interval_s = poll_interval_s
        self.timeout_s = timeout_s
        self.resolution = resolution
        self.produced_video_by_shot_id: dict[str, Any] = {}

        if client is not None:
            self._client = client
            return

        try:
            from google import genai  # lazy import: optional dependency
        except ImportError as exc:
            raise RuntimeError(
                "VeoBackend requires the 'google-genai' package: "
                "pip install google-genai. See "
                "https://ai.google.dev/gemini-api/docs/video for setup."
            ) from exc

        api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError(
                "VeoBackend requires a Veo API key: set GEMINI_API_KEY (or "
                "GOOGLE_API_KEY) in the environment, or pass api_key=... "
                "explicitly. See https://ai.google.dev/gemini-api/docs/video "
                "for setup."
            )

        self._client = genai.Client(api_key=api_key)

    def _load_reference_images(self, reference_image_ids: list[str]) -> tuple[list[dict], list[str]]:
        """Treat each reference id as a local file path. Existing files load
        as an ImageDict-shaped dict; anything else (e.g. our Bible's
        placeholder ids) is skipped and reported back for a warning.
        """
        loaded: list[dict] = []
        dropped: list[str] = []
        for ref in reference_image_ids[:VEO_MAX_REFERENCE_IMAGES]:
            if not os.path.isfile(ref):
                dropped.append(ref)
                continue
            with open(ref, "rb") as f:
                image_bytes = f.read()
            mime_type, _ = mimetypes.guess_type(ref)
            loaded.append(
                {"image_bytes": image_bytes, "mime_type": mime_type or "application/octet-stream"}
            )
        return loaded, dropped

    def render(
        self,
        prompt: VeoPrompt,
        *,
        extend_from: Optional[str] = None,
        in_multishot_chain: bool = False,
    ) -> RenderResult:
        if extend_from is not None:
            return self._render_extension(
                prompt, extend_from=extend_from, in_multishot_chain=in_multishot_chain
            )
        return self._render_standalone(prompt, in_multishot_chain=in_multishot_chain)

    def _poll_and_download(self, operation: Any, *, shot_id: str) -> Any:
        """Poll `operation` until done, download its first generated video, and
        return the SDK's Video object (not yet saved to disk).
        """
        deadline = time.monotonic() + self.timeout_s
        while not operation.done:
            if time.monotonic() > deadline:
                raise TimeoutError(f"Veo render for shot {shot_id} did not finish within {self.timeout_s}s")
            time.sleep(self.poll_interval_s)
            operation = self._client.operations.get(operation)

        generated_video = operation.response.generated_videos[0]
        self._client.files.download(file=generated_video.video)
        return generated_video.video

    def _resolve_resolution(self, *, in_multishot_chain: bool, warnings: list[str]) -> str:
        """A chain's head must render at 720p so it (and its extensions) stay
        extendable; flag it if that overrides a higher configured default.
        """
        if in_multishot_chain and self.resolution != DEFAULT_VEO_RESOLUTION:
            warnings.append(
                f"resolution forced from {self.resolution} to {DEFAULT_VEO_RESOLUTION}: shots in "
                "a multi-shot extend-chain must render at 720p to stay extendable."
            )
            return DEFAULT_VEO_RESOLUTION
        if in_multishot_chain:
            return DEFAULT_VEO_RESOLUTION
        return self.resolution

    def _render_standalone(self, prompt: VeoPrompt, *, in_multishot_chain: bool) -> RenderResult:
        warnings: list[str] = []
        resolution = self._resolve_resolution(in_multishot_chain=in_multishot_chain, warnings=warnings)

        reference_images, dropped_refs = self._load_reference_images(prompt.reference_images)
        for ref in dropped_refs:
            warnings.append(f"reference image not loadable as a local file, skipped: {ref}")

        duration_s = prompt.duration_s
        if reference_images or resolution in _VEO_HIGH_RESOLUTIONS:
            if duration_s != VEO_MAX_DURATION_S:
                warnings.append(
                    f"duration coerced from {duration_s}s to {VEO_MAX_DURATION_S}s: Veo "
                    "requires 8s clips when reference images or resolution above 720p "
                    "are used."
                )
            duration_s = VEO_MAX_DURATION_S

        config: dict[str, Any] = {
            "aspect_ratio": prompt.aspect_ratio,
            "resolution": resolution,
            "duration_seconds": duration_s,
        }
        if reference_images:
            config["reference_images"] = [
                {"image": image, "reference_type": "asset"} for image in reference_images
            ]
        if prompt.negative_prompt:
            config["negative_prompt"] = prompt.negative_prompt

        raw: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt.prompt,
            "negative_prompt": prompt.negative_prompt or None,
            "aspect_ratio": prompt.aspect_ratio,
            "resolution": resolution,
            "duration_s": duration_s,
            "reference_image_count": len(reference_images),
            "extend_from": None,
            "in_multishot_chain": in_multishot_chain,
            "extension": False,
            "warnings": warnings,
        }

        try:
            operation = self._client.models.generate_videos(
                model=self.model,
                prompt=prompt.prompt,
                image=None,
                config=config,
            )
            raw["operation_name"] = getattr(operation, "name", None)

            video = self._poll_and_download(operation, shot_id=prompt.shot_id)
            self.produced_video_by_shot_id[prompt.shot_id] = video

            os.makedirs(self.out_dir, exist_ok=True)
            out_path = os.path.join(self.out_dir, f"{prompt.shot_id}.mp4")
            video.save(out_path)

            return RenderResult(
                shot_id=prompt.shot_id,
                status="succeeded",
                backend=self.name,
                uri=out_path,
                raw=raw,
            )
        except Exception as exc:
            raw["error"] = str(exc)
            return RenderResult(
                shot_id=prompt.shot_id,
                status="failed",
                backend=self.name,
                uri=None,
                raw=raw,
            )

    def _render_extension(
        self, prompt: VeoPrompt, *, extend_from: str, in_multishot_chain: bool
    ) -> RenderResult:
        raw: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt.prompt,
            "extend_from": extend_from,
            "in_multishot_chain": in_multishot_chain,
            "extension": True,
            "resolution": DEFAULT_VEO_RESOLUTION,
        }

        predecessor_video = self.produced_video_by_shot_id.get(extend_from)
        if predecessor_video is None:
            raw["error"] = (
                f"no cached Veo video for predecessor shot {extend_from!r} (it may have "
                "failed to render); cannot extend."
            )
            return RenderResult(
                shot_id=prompt.shot_id,
                status="failed",
                backend=self.name,
                uri=None,
                raw=raw,
            )

        config = {"number_of_videos": 1, "resolution": DEFAULT_VEO_RESOLUTION}
        try:
            operation = self._client.models.generate_videos(
                model=self.model,
                prompt=prompt.prompt,
                video=predecessor_video,
                config=config,
            )
            raw["operation_name"] = getattr(operation, "name", None)

            video = self._poll_and_download(operation, shot_id=prompt.shot_id)
            self.produced_video_by_shot_id[prompt.shot_id] = video

            os.makedirs(self.out_dir, exist_ok=True)
            out_path = os.path.join(self.out_dir, f"{prompt.shot_id}.mp4")
            video.save(out_path)

            return RenderResult(
                shot_id=prompt.shot_id,
                status="succeeded",
                backend=self.name,
                uri=out_path,
                raw=raw,
            )
        except Exception as exc:
            raw["error"] = str(exc)
            return RenderResult(
                shot_id=prompt.shot_id,
                status="failed",
                backend=self.name,
                uri=None,
                raw=raw,
            )
