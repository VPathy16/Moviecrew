"""Video rendering backends: turn a VeoPrompt into a rendered (or stubbed) clip.

VideoBackend is the seam between the orchestrator and an actual video API.
StubVideoBackend never touches the network: it only builds and records the
request payload a real backend would send, so the pipeline stays fully
testable offline. VeoBackend will talk to the real Veo API once the
`google-genai` SDK and credentials are available; it imports the SDK
lazily so this module always imports cleanly without it installed.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

from .schema import VeoPrompt

# See https://ai.google.dev/gemini-api/docs/video for the current Veo model
# catalog; pin a default here so callers don't have to know the exact id.
DEFAULT_VEO_MODEL = "veo-3.1-generate-preview"


@dataclass
class RenderResult:
    shot_id: str
    status: str  # "stubbed" | "succeeded" | "failed" | ...
    backend: str
    uri: Optional[str] = None
    raw: Optional[dict[str, Any]] = None


def build_request(prompt: VeoPrompt, *, model: str = DEFAULT_VEO_MODEL) -> dict[str, Any]:
    """The backend-agnostic request payload every VideoBackend builds from a VeoPrompt."""
    return {
        "model": model,
        "prompt": prompt.prompt,
        "negative_prompt": prompt.negative_prompt,
        "duration_s": prompt.duration_s,
        "aspect_ratio": prompt.aspect_ratio,
        "reference_images": list(prompt.reference_images),
    }


class VideoBackend(ABC):
    """Renders one VeoPrompt into a clip (or a stand-in result)."""

    name: str = ""

    @abstractmethod
    def render(self, prompt: VeoPrompt) -> RenderResult:
        raise NotImplementedError


class StubVideoBackend(VideoBackend):
    """Offline backend: builds the request a real backend would send and
    returns it unsent, so the pipeline can be exercised with no network
    access and no API key.
    """

    name = "stub"

    def __init__(self, model: str = DEFAULT_VEO_MODEL) -> None:
        self.model = model

    def render(self, prompt: VeoPrompt) -> RenderResult:
        request = build_request(prompt, model=self.model)
        return RenderResult(
            shot_id=prompt.shot_id,
            status="stubbed",
            backend=self.name,
            uri=None,
            raw=request,
        )


class VeoBackend(VideoBackend):
    """Renders via the real Veo API (google-genai SDK).

    The SDK is imported lazily inside __init__ so this module always
    imports cleanly without it installed; instantiating without the SDK
    or an API key raises a clear error naming exactly what's missing.
    """

    name = "veo"

    def __init__(self, model: str = DEFAULT_VEO_MODEL, *, api_key: Optional[str] = None) -> None:
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

        self.model = model
        self._client = genai.Client(api_key=api_key)

    def render(self, prompt: VeoPrompt) -> RenderResult:
        build_request(prompt, model=self.model)

        # TODO: the exact generate-video call isn't wired up yet — the
        # google-genai Veo config field names for negative_prompt,
        # duration_s, aspect_ratio, and reference images aren't pinned down
        # here. Confirm the real kwargs against
        # https://ai.google.dev/gemini-api/docs/video before implementing
        # this call, rather than guessing them.
        raise NotImplementedError(
            "VeoBackend.render is not wired to the real Veo API yet; see "
            "the TODO in moviecrew/video.py and "
            "https://ai.google.dev/gemini-api/docs/video"
        )
