"""Deterministic, backend-agnostic guardrails layered on top of LLM output.

These never call an LLM: they enforce the schema's hard constraints (the
Veo reference-image cap) and flag known Veo failure modes (on-screen text,
crowded action, extreme close-ups) so continuity warnings don't depend on
a model remembering to mention them.
"""

from __future__ import annotations

import re

from .schema import (
    VEO_MAX_CHAIN_SEGMENTS,
    VEO_MAX_REFERENCE_IMAGES,
    Bible,
    ContinuityFlag,
    Scene,
    Shot,
)

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


def normalize_chains(
    shots: list[Shot], order: list[str], raw_chains: list[list[str]]
) -> list[list[str]]:
    """Turn the editor's raw chain grouping into something deterministic and
    Veo-legal.

    Drops unknown shot ids, sorts each chain's members by their position in
    `order`, splits any chain longer than VEO_MAX_CHAIN_SEGMENTS into
    consecutive sub-chains, assigns every shot in `order` that the editor
    left ungrouped to its own singleton chain, and returns chains ordered by
    the order-index of their first member.
    """
    valid_ids = {shot.id for shot in shots} & set(order)
    index_by_id = {shot_id: i for i, shot_id in enumerate(order)}

    assigned: set[str] = set()
    chains: list[list[str]] = []
    for raw_chain in raw_chains:
        members = [
            shot_id
            for shot_id in raw_chain
            if shot_id in valid_ids and shot_id not in assigned
        ]
        if not members:
            continue
        members.sort(key=lambda shot_id: index_by_id[shot_id])
        assigned.update(members)
        chains.append(members)

    for shot_id in order:
        if shot_id in valid_ids and shot_id not in assigned:
            chains.append([shot_id])
            assigned.add(shot_id)

    split_chains: list[list[str]] = []
    for chain in chains:
        for start in range(0, len(chain), VEO_MAX_CHAIN_SEGMENTS):
            split_chains.append(chain[start : start + VEO_MAX_CHAIN_SEGMENTS])

    split_chains.sort(key=lambda chain: index_by_id[chain[0]])
    return split_chains
