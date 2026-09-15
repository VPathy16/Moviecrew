"""Image-generation provider abstraction.

Mirrors the shape of moviecrew.reference (ReferenceImageProvider) but is
used at generation time: given a still-frame prompt and a shot id, returns
raw PNG bytes.  NullImageProvider is the default (offline safe); the real
providers (Imagen, Stable Diffusion, …) live here as they land.
"""

from __future__ import annotations

import struct
import zlib
from abc import ABC, abstractmethod


def _solid_png(rgb: tuple[int, int, int], size: int = 8) -> bytes:
    """Build a minimal, valid solid-color PNG without a Pillow dependency."""

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data))

    row = bytes(rgb) * size
    raw = b"".join(b"\x00" + row for _ in range(size))
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw))
        + chunk(b"IEND", b"")
    )


class ImageProvider(ABC):
    """Return raw image bytes for a given prompt and shot id."""

    # Set to True on real generators: approve() will prepend the board image
    # to shot.reference_image_ids so subsequent renders can anchor
    # character consistency off the approved frame.  False on Null/Mock to
    # avoid overwriting hand-supplied library stills during offline tests.
    promotes_references: bool = False

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

    # Solid ink-panel-colored placeholder, valid and decodable.
    _BYTES: bytes = _solid_png((0x24, 0x27, 0x2d))

    def generate(self, prompt: str, shot_id: str) -> bytes:
        return self._BYTES
