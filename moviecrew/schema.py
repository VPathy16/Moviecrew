"""Core data model for MovieCrew.

Stdlib-only dataclasses describing the pipeline's shared vocabulary: a
project's "Bible" (locked characters/locations/style — the consistency
layer), its scenes and shots, the Veo prompts generated per shot, and the
continuity flags / render plan produced downstream. No third-party
dependencies here so this module always imports, even without the
`anthropic` extra installed.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Optional

# --- Veo constraints -------------------------------------------------------

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
class Bible:
    style: str
    palette: str
    mood: str
    characters: list[Character] = field(default_factory=list)
    locations: list[Location] = field(default_factory=list)


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
class VeoPrompt:
    shot_id: str
    prompt: str
    negative_prompt: str = ""
    duration_s: int = VEO_MAX_DURATION_S
    aspect_ratio: str = "16:9"
    reference_images: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.duration_s = clamp_duration(self.duration_s)
        if self.aspect_ratio not in VEO_ASPECT_RATIOS:
            raise ValueError(
                f"prompt for shot {self.shot_id}: aspect_ratio must be one of "
                f"{VEO_ASPECT_RATIOS}"
            )


@dataclass
class ContinuityFlag:
    target: str
    kind: str  # "info" | "warning" | "error"
    message: str


@dataclass
class RenderPlan:
    prompts: list[VeoPrompt] = field(default_factory=list)
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
