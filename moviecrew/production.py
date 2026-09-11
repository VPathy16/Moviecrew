"""Resolving canonical production state at the moment of execution.

The pipeline holds a shot's creative intent (`ShotIntent`) separately from
the mutable state attached to it — chiefly `Shot.reference_image_ids`, which
storyboard approval rewrites. Keeping two copies of that state is how a
"canonical" representation quietly stops being canonical: an intent built at
plan time carries the references that existed then, a board is approved
afterwards, and the render goes out anchored to the wrong stills without
anything appearing to be wrong.

So execution adapters do not read stored copies. They resolve from the live
project, here, at the moment they build a request:

    project + shot_id  ->  ShotState  ->  adapter  ->  backend request

`ShotState` is deliberately a read-only view rather than a new home for
state. It owns nothing; it collects what a request needs from where that
thing actually lives, and it is built fresh per request so it cannot go
stale. When the production graph arrives (roadmap item 3) this is where
lineage and revision resolution attach.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .schema import Project, Shot, ShotIntent


class UnknownShot(LookupError):
    """A shot id that the project does not contain."""


@dataclass(frozen=True)
class ShotState:
    """Everything an execution adapter needs for one shot, resolved now.

    `reference_images` is read off the `Shot` at construction, so a board
    approved a second ago is reflected and a board approved a second from
    now is not — which is the correct behaviour for a request that is about
    to be sent.
    """

    shot: Shot
    intent: ShotIntent
    reference_images: list[str]

    @property
    def shot_id(self) -> str:
        return self.shot.id


def find_shot(project: Project, shot_id: str) -> Optional[Shot]:
    for scene in project.scenes:
        for shot in scene.shots:
            if shot.id == shot_id:
                return shot
    return None


def find_intent(project: Project, shot_id: str) -> Optional[ShotIntent]:
    plan = project.render_plan
    if plan is None:
        return None
    return next((intent for intent in plan.intents if intent.shot_id == shot_id), None)


def resolve_shot(project: Project, shot_id: str) -> ShotState:
    """Collect the current state of one shot for execution.

    Raises `UnknownShot` rather than returning a half-populated state: a
    render request built around a shot the project does not contain is a
    bug, and failing here names it while it is still cheap.

    A shot with no intent yet (the plan has not run) falls back to an intent
    synthesized from the shot itself, so previz and manual renders work
    before the prompter has ever been called.
    """
    shot = find_shot(project, shot_id)
    if shot is None:
        raise UnknownShot(f"project has no shot {shot_id!r}")

    intent = find_intent(project, shot_id) or intent_from_shot(shot)
    return ShotState(
        shot=shot,
        intent=intent,
        reference_images=list(shot.reference_image_ids),
    )


def intent_from_shot(shot: Shot) -> ShotIntent:
    """A minimal intent for a shot the prompter has not written yet.

    Uses the shot's own description rather than inventing one, so what goes
    to a backend is still traceable to something a human or an agent wrote.
    """
    return ShotIntent(
        shot_id=shot.id,
        description=shot.description,
        duration_s=shot.duration_s,
    )


def resolve_all(project: Project) -> list[ShotState]:
    """Every shot in the project, in scene/shot order."""
    return [
        resolve_shot(project, shot.id)
        for scene in project.scenes
        for shot in scene.shots
    ]
