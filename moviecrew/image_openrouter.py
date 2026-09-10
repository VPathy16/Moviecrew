"""ImageProvider backed by OpenRouter, for the storyboard gate.

Completes the routing: the agents' text and the storyboard's stills go
through one key and one bill, alongside the render backend.

OpenRouter returns generated images through the ordinary chat-completions
endpoint — an image model is asked for `modalities: ["image", "text"]` and
answers with `message.images`, each a data URI. There is no separate image
endpoint to call.

`promotes_references = True`, because this is a real generator: an approved
board frame here is a genuine likeness worth anchoring later renders to,
which is exactly what `StudioSession.approve()` gates on. The mock provider
leaves that False so an offline board approval never overwrites a
hand-supplied library still.

stdlib `urllib` again, for the reason the rest of the package uses it: no
third-party imports means MovieCrew drops into Blender's bundled Python
with nothing to install.
"""

from __future__ import annotations

import base64
import binascii
import json
import os
import urllib.error
import urllib.request
from typing import Any, Callable, Optional

from .image import ImageProvider

API_ROOT = "https://openrouter.ai/api/v1"
API_KEY_ENV = "OPENROUTER_API_KEY"
DEFAULT_MODEL = "google/gemini-2.5-flash-image"

_DATA_URI_PREFIX = "data:"


class ImageError(RuntimeError):
    """An image that could not be generated."""


def _urllib_transport(
    method: str, url: str, headers: dict[str, str], body: Optional[dict]
) -> dict[str, Any]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            return json.loads(response.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:400]
        raise ImageError(f"{method} {url} failed ({exc.code}): {detail}") from exc
    except urllib.error.URLError as exc:
        raise ImageError(f"{method} {url} unreachable: {exc.reason}") from exc


def decode_data_uri(uri: str) -> bytes:
    """The bytes behind a `data:image/png;base64,...` URI.

    Kept separate and pure so the parsing is testable without a network
    call, and so a malformed URI fails here with a clear message rather
    than as a corrupt file on disk much later.
    """
    if not uri.startswith(_DATA_URI_PREFIX) or "," not in uri:
        raise ImageError(f"not a data URI: {uri[:60]!r}")
    header, _, payload = uri.partition(",")
    if ";base64" not in header:
        raise ImageError(f"data URI is not base64: {header[:60]!r}")
    try:
        return base64.b64decode(payload, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ImageError(f"data URI payload is not valid base64: {exc}") from exc


def image_uri_of(payload: dict[str, Any]) -> str:
    """Dig the generated image out of a chat-completions response."""
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ImageError(f"no choices in response: {json.dumps(payload)[:300]}")

    message = choices[0].get("message") or {}
    images = message.get("images")
    if isinstance(images, list) and images:
        first = images[0]
        if isinstance(first, str):
            return first
        if isinstance(first, dict):
            url = (first.get("image_url") or {}).get("url") or first.get("url")
            if isinstance(url, str):
                return url

    # A model that produced no image usually explains itself in the text —
    # a refusal, a safety block, a prompt it could not render. Surfacing
    # that beats "no images in response".
    content = message.get("content")
    if isinstance(content, str) and content.strip():
        raise ImageError(f"no image returned; the model said: {content[:200]}")
    raise ImageError(f"no image in response: {json.dumps(payload)[:300]}")


class OpenRouterImageProvider(ImageProvider):
    """Storyboard stills, generated through OpenRouter."""

    name = "openrouter"
    promotes_references = True

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

        self._api_key = api_key or os.environ.get(API_KEY_ENV, "")
        if not self._api_key and transport is None:
            raise ImageError(
                f"OpenRouterImageProvider needs an API key: set {API_KEY_ENV} in "
                "the environment, or pass api_key=... explicitly."
            )

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self._referer,
            "X-Title": self._title,
        }

    def build_request(self, prompt: str) -> dict[str, Any]:
        """The request body for one still. Pure, so tests can assert on it."""
        return {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "modalities": ["image", "text"],
        }

    def generate(self, prompt: str, shot_id: str) -> bytes:
        payload = self._transport(
            "POST", f"{self.api_root}/chat/completions", self._headers(), self.build_request(prompt)
        )
        if isinstance(payload.get("error"), dict):
            message = payload["error"].get("message", "unknown error")
            raise ImageError(f"{self.model} failed for {shot_id}: {message}")
        return decode_data_uri(image_uri_of(payload))
