"""Deterministic, backend-agnostic guardrails layered on top of LLM output.

These never call an LLM, and they never apply a backend's limits — no
duration is snapped and no reference list is truncated here, because at this
point in the pipeline no backend has been chosen to have limits. What they
do is decide things the production owns (which shots are consistency
anchors, what order the film runs in, which shots form a continuous take)
and warn about failure modes common to generative video, so continuity
warnings don't depend on a model remembering to mention them.
"""

from __future__ import annotations

import os
import re

from .schema import (
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

    Consistency within a continuous take comes from the take itself; a hard
    cut (a chain's first shot) is where a character can drift, so that is
    where reference images get attached. Every other shot is explicitly
    unanchored with no reference ids, overwriting whatever the
    cinematographer agent guessed.

    This decides two things and no others: whether a shot is an anchor, and
    which references belong to it. It does not touch duration and does not
    truncate the reference list. Veo, for instance, needs 8s clips when
    references are present and accepts three of them — but that is applied
    by `VeoBackend.adapt()` at the execution boundary. Forcing it here would
    rewrite the production's intent to suit one backend before a backend had
    even been chosen.
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
        head.reference_image_ids = refs
        anchor_shot_ids.add(head_id)

    for shot in shots_by_id.values():
        if shot.id in anchor_shot_ids:
            continue
        shot.consistency_anchor = False
        shot.reference_image_ids = []


def generative_video_flags(prompt_text: str, shot: Shot) -> list[ContinuityFlag]:
    """Flag failure modes common to generative video that no field captures.

    These are not one vendor's quirks. Legible on-screen text, crowded
    multi-person action and extreme close-ups on faces degrade across every
    generative video model we have tried, so the warning is worth raising
    before a backend has been chosen.

    A lint, deliberately: it reads a shot's text and warns, but never
    constrains what a `ShotIntent` may say. A specific backend's actual
    limits are applied by that backend's `adapt()` at the execution
    boundary, and nowhere else.
    """
    flags: list[ContinuityFlag] = []

    if _ON_SCREEN_TEXT_RE.search(prompt_text):
        flags.append(
            ContinuityFlag(
                target=shot.id,
                kind="warning",
                message=(
                    "Prompt may request on-screen text, which generative video "
                    "renders poorly."
                ),
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
                message="Extreme close-up on a face is prone to facial-distortion artifacts.",
            )
        )

    return flags


def normalize_order(shots: list[Shot], raw_order: list[str]) -> list[str]:
    """A deterministic screening order containing every shot exactly once.

    The editor's output is a proposal from a language model, so it is not
    trusted as given: unknown ids are dropped, duplicates collapse to their
    first appearance, and any shot the editor forgot is appended in the
    order the scenes and shots were written. What survives is the editor's
    intent where it was valid, and a total order regardless — a shot that
    silently vanished from `order` would silently vanish from the film.
    """
    valid_ids = {shot.id for shot in shots}

    order: list[str] = []
    seen: set[str] = set()
    for shot_id in raw_order:
        if shot_id in valid_ids and shot_id not in seen:
            seen.add(shot_id)
            order.append(shot_id)

    for shot in shots:
        if shot.id not in seen:
            seen.add(shot.id)
            order.append(shot.id)

    return order


def normalize_chains(
    shots: list[Shot], order: list[str], raw_chains: list[list[str]]
) -> list[list[str]]:
    """Turn the editor's raw chain grouping into deterministic editorial chains.

    A chain is a creative statement — these shots are one continuous take —
    and it is kept whole however long it runs. Backends disagree about how
    much of a continuous take they can execute in one piece (Veo carries 21
    segments per extend-run; a live-action unit just rolls), so that
    segmentation belongs to the backend, which answers for itself via
    `VideoBackend.segment()`. Cutting the canonical chain here would make an
    editorial decision on behalf of whichever backend happened to be
    configured.

    Drops unknown shot ids, sorts each chain's members by their position in
    `order`, assigns every shot in `order` that the editor left ungrouped to
    its own singleton chain, and returns chains ordered by the order-index
    of their first member.
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

    chains.sort(key=lambda chain: index_by_id[chain[0]])
    return chains
