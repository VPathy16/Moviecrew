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
from dataclasses import asdict, dataclass, field, fields as dataclass_fields
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


# --- Cinematography Intelligence Layer --------------------------------------
#
# Structured cinematography beside Shot's existing prose fields (camera_move,
# lens, framing) — the seam those fields' own history anticipated: a
# machine-readable layer that can be validated, searched and eventually
# compiled per-provider, while the prose stays what models actually read.
# Entirely optional throughout; a Shot without a cinematic_spec behaves
# exactly as it always has. Technique ids referenced here (composition.
# techniques, technique_ids) come from moviecrew.cinematography.TECHNIQUES —
# not enforced here (schema.py stays a pure data layer; cross-referencing
# the technique graph is a deterministic-guardrail concern, done in crew.py
# the same way duration/continuity checks are).


@dataclass
class CameraSpec:
    shot_scale_start: str = ""
    shot_scale_end: str = ""
    angle: str = ""
    movement_type: str = ""
    movement_speed: str = ""
    movement_motivation: str = ""
    lens_mm: Optional[int] = None


@dataclass
class FocusSpec:
    mode: str = ""  # deep | shallow | rack | ''
    rack_from: str = ""
    rack_to: str = ""


@dataclass
class LightingSpec:
    key: str = ""
    contrast: str = ""  # high_key | low_key
    continuity_locked: bool = False


@dataclass
class CompositionSpec:
    techniques: list[str] = field(default_factory=list)  # technique ids


@dataclass
class AcceptanceSpec:
    """What a generated take must/should/must-not satisfy to be accepted.

    Evidence for a future evaluator (CIL Phase 4), not enforced by anything
    today — recording it now costs nothing and means it doesn't have to be
    reconstructed later from a shot's prose after the fact.
    """

    must: list[str] = field(default_factory=list)
    prefer: list[str] = field(default_factory=list)
    avoid: list[str] = field(default_factory=list)


@dataclass
class CinematicSpec:
    camera: CameraSpec = field(default_factory=CameraSpec)
    focus: FocusSpec = field(default_factory=FocusSpec)
    lighting: LightingSpec = field(default_factory=LightingSpec)
    composition: CompositionSpec = field(default_factory=CompositionSpec)
    acceptance: AcceptanceSpec = field(default_factory=AcceptanceSpec)
    # Every technique id chosen for this shot, flattened across the nested
    # fields above too, so a caller can check conflicts/intent-support
    # without re-walking each one.
    technique_ids: list[str] = field(default_factory=list)
    narrative_intents: list[str] = field(default_factory=list)
    rationale: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "CinematicSpec":
        """Build from a Cinematographer's raw dict for it, the same way
        crew._shot_from_raw builds a Shot: filtered to each nested
        dataclass's own declared fields, never `Cls(**raw)` directly. The
        agent is a language model, and harmless extra metadata alongside a
        known key ("note", "reasoning", ...) is routine, not exceptional —
        `CameraSpec(**raw)` would crash the whole pipeline on it instead of
        silently ignoring it, exactly the failure this pattern exists to
        avoid elsewhere in the schema/crew boundary.
        """

        def sub(target_cls, key):
            raw = data.get(key)
            raw = raw if isinstance(raw, dict) else {}
            names = {f.name for f in dataclass_fields(target_cls)}
            return target_cls(**{k: v for k, v in raw.items() if k in names})

        def as_list(value):
            return [str(v) for v in value] if isinstance(value, list) else []

        camera = sub(CameraSpec, "camera")
        if camera.lens_mm is not None:
            try:
                camera.lens_mm = int(camera.lens_mm)
            except (TypeError, ValueError):
                camera.lens_mm = None

        # Field-name filtering (sub()) stops an unexpected key from crashing
        # construction, but not an expected key holding the wrong container
        # type (a string where a list was asked for) — coerce every list[str]
        # field the same way technique_ids/narrative_intents are below, so a
        # composition/acceptance typo degrades to an empty list instead of
        # iterating a string's characters downstream.
        composition = sub(CompositionSpec, "composition")
        composition.techniques = as_list(composition.techniques)
        acceptance = sub(AcceptanceSpec, "acceptance")
        acceptance.must = as_list(acceptance.must)
        acceptance.prefer = as_list(acceptance.prefer)
        acceptance.avoid = as_list(acceptance.avoid)

        return cls(
            camera=camera,
            focus=sub(FocusSpec, "focus"),
            lighting=sub(LightingSpec, "lighting"),
            composition=composition,
            acceptance=acceptance,
            technique_ids=as_list(data.get("technique_ids")),
            narrative_intents=as_list(data.get("narrative_intents")),
            rationale=str(data.get("rationale") or ""),
        )


# --- Scenes / Shots ----------------------------------------------------------


@dataclass
class Beat:
    """One timed micro-action inside a shot's duration.

    Shots are the unit of narrative structure (and of generation); beats are
    the unit of physical detail inside one. A shot with several beats is
    still one shot — a subject's eyes moving, then their expression
    changing, then their body turning, are beats of a single 6-second shot,
    not a reason to split it into three. Only `Shot.cut_reason` on the
    *next* shot creates a new one.
    """

    start_s: float
    end_s: float
    action: str

    def __post_init__(self) -> None:
        if self.end_s <= self.start_s:
            raise ValueError(
                f"beat end_s ({self.end_s}) must be after start_s ({self.start_s})"
            )
        if not isinstance(self.action, str) or not self.action.strip():
            raise ValueError("beat needs a non-empty action")


@dataclass
class Shot:
    """One shot as the production intends it — not as a backend can render it.

    `duration_s` is a float, not snapped to any backend's legal clip
    lengths here — a pipeline that rounds it on the way in has destroyed
    information before anyone chose what would render the shot. It is,
    however, subject to a pacing policy the pipeline enforces one layer up
    (`crew.py`'s MIN_SHOT_DURATION_S/MAX_SHOT_DURATION_S, currently 5-15s):
    not a backend quirk, but a product decision that a shot shorter than a
    real cut or longer than good pacing should never reach a backend at
    all. Not checked here, for the same reason cut_reason isn't: enforcing
    it needs the bounded-retry-then-clamp handling `crew.py` already does
    for its shots as a scene, not a hard crash on one shot in isolation.

    `reference_image_ids` is likewise uncapped. A backend that accepts three
    references truncates to three at its own boundary; the shot keeps what
    the production attached to it.

    `beats` is optional temporal detail inside this one shot — see `Beat`.
    `cut_reason` names the editorial reason a *new* shot starts here (a
    reveal, a POV change, a reaction, a geography change, ...); it is
    required for every shot after a scene's first, enforced once a scene's
    shots are assembled (a shot in isolation cannot know its own position
    within its scene, so this is not checked in `__post_init__`).
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
    visible_character_ids: Optional[list[str]] = None
    visible_prop_ids: Optional[list[str]] = None
    image_prompt: str = ""
    consistency_anchor: bool = False
    story_contract_version: int = 0  # 0: legacy, 1: explicit causal direction
    purpose: str = ''
    action: str = ''
    entry_state: dict[str, str] = field(default_factory=dict)
    exit_state: dict[str, str] = field(default_factory=dict)
    screen_direction: str = ''
    audio_intent: str = ''
    transition: str = 'cut'  # cut | continuous | ellipsis
    cinematic_spec: Optional[CinematicSpec] = None
    beats: list[Beat] = field(default_factory=list)
    cut_reason: str = ''


    def __post_init__(self) -> None:
        if self.story_contract_version not in (0, 1):
            raise ValueError('Unsupported story contract version')
        if self.story_contract_version == 1 and self.transition not in ('cut', 'continuous', 'ellipsis'):
            raise ValueError('Unknown shot transition')
        if self.story_contract_version == 1:
            if not isinstance(self.purpose, str) or not self.purpose.strip() or not isinstance(self.action, str) or not self.action.strip():
                raise ValueError(f'Shot {self.id} needs a purpose and observable action')
            for state in (self.entry_state, self.exit_state):
                if not isinstance(state, dict) or not state or any(not isinstance(k, str) or not isinstance(v, str) or not k.strip() or not v.strip() for k, v in state.items()):
                    raise ValueError(f'Shot {self.id} needs named entry and exit states')
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
    event: str = ''
    goal: str = ''
    obstacle: str = ''
    turning_point: str = ''
    acting_tasks: dict[str, str] = field(default_factory=dict)
    # How long this scene's shots should sum to, in seconds. None (the
    # default, and every pre-existing project) means no budget is enforced —
    # the cinematographer plans freely, exactly as before this field existed.
    target_duration_s: Optional[float] = None


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
    compiler_version: str = 'legacy'
    direction_context: dict = field(default_factory=dict)

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
    editorial_notes: dict[str, str] = field(default_factory=dict)


# --- Project (top-level container) ------------------------------------------


@dataclass
class Project:
    title: str
    logline: str
    bible: Bible
    outline: list[str] = field(default_factory=list)
    scenes: list[Scene] = field(default_factory=list)
    render_plan: Optional[RenderPlan] = None
    sheet_notes: dict[str, dict[str, str]] = field(default_factory=dict)
    # The whole film's requested runtime, if the brief asked for one. None
    # for every pre-existing project. Divided across scenes (see crew.make)
    # as each Scene's own target_duration_s; kept here too so the number
    # that was actually asked for survives independently of how it was split.
    target_duration_s: Optional[float] = None

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)
