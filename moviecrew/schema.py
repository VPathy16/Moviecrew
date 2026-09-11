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

ASPECT_RATIO_RE = re.compile(r"^\d+:\d+$")


# --- Veo constraints -------------------------------------------------------
#
# One backend's limits, kept here because several modules still read them.
# They constrain `video.veo_prompt()` at the execution boundary, never
# `ShotIntent` — see its docstring.

# Legal clip lengths for Veo 3/3.1; 8s is the max for standard generation.
VEO_LEGAL_DURATIONS_S: tuple[int, ...] = (4, 6, 8)
VEO_MAX_DURATION_S: int = max(VEO_LEGAL_DURATIONS_S)
VEO_MIN_DURATION_S: int = min(VEO_LEGAL_DURATIONS_S)
VEO_MAX_REFERENCE_IMAGES: int = 3
VEO_ASPECT_RATIOS: tuple[str, ...] = ("16:9", "9:16")

# Veo extends a clip by continuing it from its final frame, up to 20 times,
# so one continuous take ("chain") is at most 1 base clip + 20 extensions.
VEO_MAX_EXTENSIONS: int = 20
VEO_MAX_CHAIN_SEGMENTS: int = VEO_MAX_EXTENSIONS + 1


def clamp_duration(seconds: float) -> int:
    """Snap an arbitrary duration to the nearest legal Veo clip length."""
    return min(VEO_LEGAL_DURATIONS_S, key=lambda legal: abs(legal - seconds))


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
    id: str
    scene_id: str
    description: str
    duration_s: int
    camera_move: str = ""
    lens: str = ""
    framing: str = ""
    reference_image_ids: list[str] = field(default_factory=list)
    first_frame_ref: Optional[str] = None
    last_frame_ref: Optional[str] = None
    consistency_anchor: bool = False

    def __post_init__(self) -> None:
        self.duration_s = clamp_duration(self.duration_s)
        if len(self.reference_image_ids) > VEO_MAX_REFERENCE_IMAGES:
            raise ValueError(
                f"shot {self.id}: at most {VEO_MAX_REFERENCE_IMAGES} reference "
                f"images allowed, got {len(self.reference_image_ids)}"
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
    shot wants, in seconds, as a float; references are however many the shot
    has. Veo's 4/6/8-second legality, its cap of three reference images, its
    two legal aspect ratios — those are applied by `video.veo_prompt()` at
    the moment a request is actually built, and a different backend applies
    its own. An intent that survives being asked for is a better record of
    what was wanted than one silently rounded on creation.

    `description` is prose today. That is a known interim state: the
    roadmap's next step turns cinematography into structure (camera
    transforms, lens, focus, composition, actor marks), and the prose
    becomes something generated from that structure for the benefit of
    models that want words.
    """

    shot_id: str
    description: str
    negative: str = ""
    duration_s: float = 8.0
    aspect_ratio: str = "16:9"
    reference_images: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.duration_s <= 0:
            raise ValueError(
                f"intent for shot {self.shot_id}: duration_s must be positive, "
                f"got {self.duration_s}"
            )
        # Shape only — which ratios are legal is a backend's business.
        if not ASPECT_RATIO_RE.match(self.aspect_ratio):
            raise ValueError(
                f"intent for shot {self.shot_id}: aspect_ratio must look like "
                f"'W:H', got {self.aspect_ratio!r}"
            )


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
    est_duration_s: int = 0


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
