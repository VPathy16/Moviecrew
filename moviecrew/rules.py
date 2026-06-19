"""Deterministic, backend-agnostic guardrails layered on top of LLM output.

These never call an LLM: they enforce the schema's hard constraints (the
Veo reference-image cap) and flag known Veo failure modes (on-screen text,
crowded action, extreme close-ups) so continuity warnings don't depend on
a model remembering to mention them.
"""

from __future__ import annotations

import re

from .schema import VEO_MAX_REFERENCE_IMAGES, Bible, ContinuityFlag, Scene, Shot

_ON_SCREEN_TEXT_RE = re.compile(
    r"\b(text|caption|subtitle|title card|sign(?:age)?|reads?:|written)\b", re.IGNORECASE
)
_CROWD_RE = re.compile(
    r"\b(crowd|group of|several people|multiple people|many people|everyone)\b", re.IGNORECASE
)


def assign_reference_images(shot: Shot, scene: Scene, bible: Bible) -> None:
    """Set shot.reference_image_ids from the Bible — the consistency lever.

    Pulls reference images from every character in `scene.character_ids`
    and the scene's location, in that order, deduplicated and capped at
    VEO_MAX_REFERENCE_IMAGES. Overwrites whatever the cinematographer agent
    guessed: the Bible is the single source of truth for what a
    character/location looks like.
    """
    images: list[str] = []

    characters_by_id = {character.id: character for character in bible.characters}
    for character_id in scene.character_ids:
        character = characters_by_id.get(character_id)
        if character is None:
            continue
        for image in character.reference_images:
            if image not in images:
                images.append(image)

    locations_by_id = {location.id: location for location in bible.locations}
    location = locations_by_id.get(scene.location_id) if scene.location_id else None
    if location is not None:
        for image in location.reference_images:
            if image not in images:
                images.append(image)

    shot.reference_image_ids = images[:VEO_MAX_REFERENCE_IMAGES]


def veo_constraint_flags(prompt_text: str, shot: Shot) -> list[ContinuityFlag]:
    """Flag known Veo failure modes that VeoPrompt itself has no field for."""
    flags: list[ContinuityFlag] = []

    if _ON_SCREEN_TEXT_RE.search(prompt_text):
        flags.append(
            ContinuityFlag(
                target=shot.id,
                kind="warning",
                message="Prompt may request on-screen text, which Veo renders poorly.",
            )
        )

    if _CROWD_RE.search(prompt_text):
        flags.append(
            ContinuityFlag(
                target=shot.id,
                kind="warning",
                message="Prompt describes complex multi-person action; consider simplifying.",
            )
        )

    if "extreme close-up" in (shot.framing or "").lower() and "face" in prompt_text.lower():
        flags.append(
            ContinuityFlag(
                target=shot.id,
                kind="warning",
                message="Extreme close-up on a face is prone to Veo facial-distortion artifacts.",
            )
        )

    return flags
