"""Deterministic, backend-agnostic guardrails layered on top of LLM output.

These never call an LLM: they enforce the schema's hard constraints (the
Veo reference-image cap) and flag known Veo failure modes (on-screen text,
crowded action, extreme close-ups) so continuity warnings don't depend on
a model remembering to mention them.
"""

from __future__ import annotations

import os
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


def select_anchors(
    scenes: list[Scene],
    chains: list[list[str]],
    bible: Bible,
    *,
    is_real=os.path.isfile,
) -> None:
    """Mark each chain's head shot as a consistency anchor when its scene has
    a character with a real reference still, and attach those stills.

    Consistency within a take comes from Veo extension (see moviecrew.video);
    a hard cut (a chain's first shot) is where a character can drift, so
    that's where reference images get attached. Veo requires 8s clips when
    reference images are present, so an anchored shot's duration is forced
    to 8. Every other shot is explicitly unanchored with no reference ids,
    overwriting whatever the cinematographer agent guessed.
    """
    shots_by_id: dict[str, Shot] = {
        shot.id: shot for scene in scenes for shot in scene.shots
    }
    scene_by_shot_id: dict[str, Scene] = {
        shot.id: scene for scene in scenes for shot in scene.shots
    }
    characters_by_id = {character.id: character for character in bible.characters}

    anchor_shot_ids: set[str] = set()
    for chain in chains:
        if not chain:
            continue
        head_id = chain[0]
        head = shots_by_id.get(head_id)
        scene = scene_by_shot_id.get(head_id)
        if head is None or scene is None:
            continue

        refs: list[str] = []
        for character_id in scene.character_ids:
            character = characters_by_id.get(character_id)
            if character is None:
                continue
            for image in character.reference_images:
                if is_real(image) and image not in refs:
                    refs.append(image)

        if not refs:
            continue

        head.consistency_anchor = True
        head.reference_image_ids = refs[:VEO_MAX_REFERENCE_IMAGES]
        head.duration_s = 8
        anchor_shot_ids.add(head_id)

    for shot in shots_by_id.values():
        if shot.id in anchor_shot_ids:
            continue
        shot.consistency_anchor = False
        shot.reference_image_ids = []


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
        members = []
        for shot_id in raw_chain:
            if shot_id in valid_ids and shot_id not in assigned:
                assigned.add(shot_id)
                members.append(shot_id)
        if not members:
            continue
        members.sort(key=lambda shot_id: index_by_id[shot_id])
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
