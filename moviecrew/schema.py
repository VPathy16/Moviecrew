"""Core data model for MovieCrew.

Stdlib-only dataclasses describing the pipeline's shared vocabulary: a
project's "Bible" (locked characters/locations/style — the consistency
layer), its scenes and shots, the backend-neutral `ShotIntent` per shot, and the
continuity flags / render plan produced downstream. No third-party
dependencies here so this module always imports, even without the
`anthropic` extra installed.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from typing import Optional

_ASPECT_RATIO_RE = re.compile(r"^(\d+):(\d+)$")

DEFAULT_ASPECT_RATIO = "16:9"


def parse_aspect_ratio(ratio: str) -> tuple[int, int]:
    """`"239:100"` -> `(239, 100)`. Raises on anything that isn't a ratio.

    Both sides must be positive: `0:0`, `16:0` and `0:9` are well-formed
    strings and meaningless as ratios, so they are refused here rather than
    surfacing as a division error inside some backend.

    Which ratios are *renderable* is a backend's business — 2.39:1
    anamorphic is a legitimate thing for a film to want, and the fact that
    one model cannot produce it is a fact about that model.
    """
    match = _ASPECT_RATIO_RE.match(ratio or "")
    if not match:
        raise ValueError(f"aspect_ratio must look like 'W:H', got {ratio!r}")
    width, height = int(match.group(1)), int(match.group(2))
    if width <= 0 or height <= 0:
        raise ValueError(f"aspect_ratio sides must both be positive, got {ratio!r}")
    return width, height


# --- Bible (consistency layer) ---------------------------------------------


@dataclass
class Character:
    id: str
    name: str
    description: str
    reference_images: list[str] = field(default_factory=list)


@dataclass
class Location:
    id: str
    name: str
    description: str
    reference_images: list[str] = field(default_factory=list)


@dataclass
class Prop:
    id: str
    name: str
    description: str
    reference_images: list[str] = field(default_factory=list)


@dataclass
class Bible:
    style: str
    palette: str
    mood: str
    characters: list[Character] = field(default_factory=list)
    locations: list[Location] = field(default_factory=list)
    props: list[Prop] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Bible":
        return cls(
            style=data["style"],
            palette=data["palette"],
            mood=data["mood"],
            characters=[Character(**c) for c in data.get("characters", [])],
            locations=[Location(**l) for l in data.get("locations", [])],
            props=[Prop(**p) for p in data.get("props", [])],
        )


# --- Scenes / Shots ----------------------------------------------------------


@dataclass
class Shot:
    """One shot as the production intends it — not as a backend can render it.

    `duration_s` is whatever the shot wants, in seconds. It is deliberately
    not snapped to any backend's legal clip lengths and deliberately a
    float: 2.5 seconds and 11.5 seconds are ordinary creative intentions,
    and a pipeline that rounds them on the way in has destroyed information
    before anyone chose what would render the shot.

    `reference_image_ids` is likewise uncapped. A backend that accepts three
    references truncates to three at its own boundary; the shot keeps what
    the production attached to it.
    """

    id: str
    scene_id: str
    description: str
    duration_s: float
    camera_move: str = ""
    lens: str = ""
    framing: str = ""
    reference_image_ids: list[str] = field(default_factory=list)
    first_frame_ref: Optional[str] = None
    last_frame_ref: Optional[str] = None
    consistency_anchor: bool = False

    def __post_init__(self) -> None:
        if self.duration_s <= 0:
            raise ValueError(
                f"shot {self.id}: duration_s must be positive, got {self.duration_s}"
            )


@dataclass
class Scene:
    id: str
    slug: str
    title: str
    summary: str
    location_id: Optional[str] = None
    character_ids: list[str] = field(default_factory=list)
    shots: list[Shot] = field(default_factory=list)


# --- Generated artifacts ----------------------------------------------------


@dataclass
class ShotIntent:
    """What a shot should be, in terms no backend owns.

    This is the pipeline's centre: what the agents produce and what every
    stage downstream consumes. It replaced `VeoPrompt`, which put one
    vendor's name and one vendor's limits at the middle of the system — so
    a shot could not be expressed without first deciding what would render
    it, and every stage inherited constraints belonging to a single model.

    Nothing here is clamped to a backend's rules. A duration is whatever the
    shot wants, in seconds, as a float, and an aspect ratio is any real
    ratio. Veo's 4/6/8-second legality, its cap of three reference images,
    its two renderable aspect ratios — those are applied by
    `video.veo_prompt()` at the moment a request is actually built, and a
    different backend applies its own. An intent that survives being asked
    for is a better record of what was wanted than one silently rounded on
    creation.

    It deliberately carries **no reference images**. Those live on the
    `Shot`, which storyboard approval mutates, and a copy taken at plan time
    goes stale the moment a board is approved. An execution adapter resolves
    them from live project state instead — see `production.resolve_shot`.
    Two mutable copies of the same production state is how a canonical
    representation stops being canonical.

    `description` is prose today. That is a known interim state: the
    roadmap's next step turns cinematography into structure (camera
    transforms, lens, focus, composition, actor marks), and the prose
    becomes something generated from that structure for the benefit of
    models that want words. Nothing here blocks that — a structured field
    can be added beside `description` and the prose derived from it.
    """

    shot_id: str
    description: str
    negative: str = ""
    duration_s: float = 8.0
    aspect_ratio: str = DEFAULT_ASPECT_RATIO

    def __post_init__(self) -> None:
        if self.duration_s <= 0:
            raise ValueError(
                f"intent for shot {self.shot_id}: duration_s must be positive, "
                f"got {self.duration_s}"
            )
        try:
            parse_aspect_ratio(self.aspect_ratio)
        except ValueError as exc:
            raise ValueError(f"intent for shot {self.shot_id}: {exc}") from exc


@dataclass
class ContinuityFlag:
    target: str
    kind: str  # "info" | "warning" | "error"
    message: str


@dataclass
class RenderPlan:
    intents: list[ShotIntent] = field(default_factory=list)
    flags: list[ContinuityFlag] = field(default_factory=list)
    order: list[str] = field(default_factory=list)
    chains: list[list[str]] = field(default_factory=list)
    est_duration_s: float = 0.0


# --- Project (top-level container) ------------------------------------------


@dataclass
class Project:
    title: str
    logline: str
    bible: Bible
    outline: list[str] = field(default_factory=list)
    scenes: list[Scene] = field(default_factory=list)
    render_plan: Optional[RenderPlan] = None

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)
