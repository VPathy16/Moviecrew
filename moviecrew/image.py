"""Image-generation provider abstraction.

Mirrors the shape of moviecrew.reference (ReferenceImageProvider) but is
used at generation time: given a still-frame prompt and a shot id, returns
raw PNG bytes.  NullImageProvider is the default (offline safe); the real
providers (Imagen, Stable Diffusion, …) live here as they land.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class ImageProvider(ABC):
    """Return raw image bytes for a given prompt and shot id."""

    @abstractmethod
    def generate(self, prompt: str, shot_id: str) -> bytes: ...


class NullImageProvider(ImageProvider):
    """Default provider: always raises.  Forces callers to opt in explicitly."""

    def generate(self, prompt: str, shot_id: str) -> bytes:
        raise NotImplementedError(
            "NullImageProvider cannot generate images; install a real provider."
        )


class MockImageProvider(ImageProvider):
    """Deterministic offline provider for tests and local demos.

    Returns a fixed stub PNG-shaped byte string for every request so callers
    can write it to disk and serve it without needing a real image API.
    """

    # Minimal 1×1 white pixel PNG (valid, 67 bytes).
    _BYTES: bytes = (
        b"\x89PNG\r\n\x1a\n"                      # PNG signature
        b"\x00\x00\x00\rIHDR"                      # IHDR chunk
        b"\x00\x00\x00\x01\x00\x00\x00\x01"        # 1x1
        b"\x08\x02\x00\x00\x00\x90wS\xde"          # 8-bit RGB + CRC
        b"\x00\x00\x00\x0cIDAT"                    # IDAT chunk
        b"x\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N"  # compressed white pixel
        b"\x00\x00\x00\x00IEND\xaeB`\x82"          # IEND
    )

    def generate(self, prompt: str, shot_id: str) -> bytes:
        return self._BYTES
