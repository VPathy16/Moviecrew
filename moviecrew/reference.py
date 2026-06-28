"""Reference-still providers: the source of the images select_anchors attaches
to chain-head shots for cross-cut character consistency (see moviecrew.rules).

ReferenceImageProvider is the seam between the pipeline and an actual image
generator. NullReferenceImageProvider (the default) never produces anything,
so the pipeline behaves exactly as before this existed. FileReferenceImageProvider
lets a user supply hand-made stills from disk ahead of PR8's real generator
(Nano Banana / Gemini image).
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Optional

from .schema import Bible, Character


class ReferenceImageProvider(ABC):
    """Produces a reference still for one character, or None if it can't."""

    @abstractmethod
    def generate(self, character: Character) -> Optional[bytes]:
        raise NotImplementedError


class NullReferenceImageProvider(ReferenceImageProvider):
    """Default provider: never produces a still. The pipeline runs exactly as
    it did before anchoring existed.
    """

    def generate(self, character: Character) -> Optional[bytes]:
        return None


class FileReferenceImageProvider(ReferenceImageProvider):
    """Reads `<directory>/<character.id>.png` if it exists; None otherwise.

    Lets a user hand-supply stills now, before PR8 wires up a real generator.
    """

    def __init__(self, directory: str) -> None:
        self.directory = directory

    def generate(self, character: Character) -> Optional[bytes]:
        path = os.path.join(self.directory, f"{character.id}.png")
        if not os.path.isfile(path):
            return None
        with open(path, "rb") as f:
            return f.read()


def populate_reference_stills(
    bible: Bible, provider: ReferenceImageProvider, *, out_dir: str
) -> list[str]:
    """Ask `provider` for a still per Bible character; write any produced
    bytes to `out_dir/<character.id>.png` and point character.reference_images
    at it. Returns the ids of characters that got a still. Never raises on a
    no-op provider (e.g. NullReferenceImageProvider).
    """
    populated: list[str] = []
    for character in bible.characters:
        still = provider.generate(character)
        if still is None:
            continue
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, f"{character.id}.png")
        with open(path, "wb") as f:
            f.write(still)
        character.reference_images = [path]
        populated.append(character.id)
    return populated
