"""Cinematography Intelligence Layer: a small, compositional technique graph.

This is deliberately NOT a clone of any third-party cinematography catalogue
(424 named techniques, authored definitions, prompts, examples). It is an
independent, minimal ontology built from standard film terminology — MVP
vocabulary sized to prove that structured intent beats free-form prompting,
not to be exhaustive. See the module docstring pattern used elsewhere in this
codebase: this graph answers "when is a technique a valid expression of a
story beat, what does it conflict with, what does it pair with" — a flat
list only answers "what is a dolly zoom?"

`Technique.id` values are the vocabulary `CinematicSpec` (see schema.py) and
the Cinematographer agent are expected to reference. Keeping the id space
here, in one place, is what lets `check_conflicts`/`techniques_for_intent`
stay meaningful instead of drifting out of sync with whatever an agent
happens to emit.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .schema import CinematicSpec, ContinuityFlag, Shot

# Narrative intents a technique can serve. Kept separate from techniques
# themselves since several techniques typically support the same intent,
# and an intent is a valid value for CinematicSpec.narrative_intents.
NARRATIVE_INTENTS = (
    "establish", "reveal", "isolate", "dominate", "intimate", "pursue",
    "disorient", "observe", "conceal", "release", "accelerate", "pause",
)


@dataclass
class Technique:
    """One node in the technique graph.

    `category` groups techniques for UI/validation purposes (shot_scale,
    angle, movement, composition, focus, lighting, edit_relation).
    `supports_intent` lists NARRATIVE_INTENTS this technique can express.
    `requires`/`conflicts_with`/`pairs_with` reference other Technique ids;
    `provider_reliability` is intentionally empty here — Phase 5 (empirical
    learning) is what would populate it from observed generation outcomes,
    not authored guesses.
    """

    id: str
    category: str
    name: str
    description: str
    supports_intent: tuple[str, ...] = ()
    requires: tuple[str, ...] = ()
    conflicts_with: tuple[str, ...] = ()
    pairs_with: tuple[str, ...] = ()
    provider_reliability: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        unknown = set(self.supports_intent) - set(NARRATIVE_INTENTS)
        if unknown:
            raise ValueError(f"technique {self.id!r} supports unknown intent(s): {sorted(unknown)}")


_TECHNIQUES: tuple[Technique, ...] = (
    # --- Shot scale -----------------------------------------------------
    Technique("ecu", "shot_scale", "Extreme close-up",
              "Frame fills with a single detail (eyes, a hand, an object) — the most intense scale available.",
              supports_intent=("intimate", "reveal", "isolate")),
    Technique("cu", "shot_scale", "Close-up",
              "Frame is the face or a small object, cropped tight — reads emotion or detail with no world around it.",
              supports_intent=("intimate", "reveal")),
    Technique("mcu", "shot_scale", "Medium close-up",
              "Chest-up framing — the standard conversational scale, close enough for expression, loose enough for gesture.",
              supports_intent=("intimate", "observe")),
    Technique("ms", "shot_scale", "Medium shot",
              "Waist-up framing — balances performance and body language with some environment.",
              supports_intent=("observe",)),
    Technique("medium_wide", "shot_scale", "Medium wide",
              "Knee-up framing — keeps full-body action readable while still showing environment.",
              supports_intent=("observe", "establish")),
    Technique("wide", "shot_scale", "Wide shot",
              "Full figure(s) within their environment — establishes spatial relationship and scale.",
              supports_intent=("establish", "isolate", "dominate")),
    Technique("establishing", "shot_scale", "Establishing shot",
              "A wide, often static view that orients the audience to a new location before narrower coverage.",
              supports_intent=("establish",), pairs_with=("wide",)),
    Technique("ots", "shot_scale", "Over-the-shoulder",
              "Foreground shoulder/head frames a second subject — ties two people into one composition for dialogue or confrontation.",
              supports_intent=("observe", "dominate")),
    Technique("insert", "shot_scale", "Insert shot",
              "A tight cutaway to an object or detail outside the main coverage — isolates one fact for the audience.",
              supports_intent=("reveal", "isolate")),
    Technique("reaction", "shot_scale", "Reaction shot",
              "Cuts to a character's face responding to an event just shown, rather than the event itself.",
              supports_intent=("intimate", "observe")),

    # --- Camera angle -----------------------------------------------------
    Technique("eye_level", "angle", "Eye level",
              "Camera at the subject's eye height — neutral, no power relation implied.",
              supports_intent=("observe",)),
    Technique("high_angle", "angle", "High angle",
              "Camera looks down on the subject — reads as vulnerability, smallness, or being observed.",
              supports_intent=("isolate", "dominate"), conflicts_with=("low_angle",)),
    Technique("low_angle", "angle", "Low angle",
              "Camera looks up at the subject — reads as power, threat, or scale.",
              supports_intent=("dominate",), conflicts_with=("high_angle",)),
    Technique("overhead", "angle", "Overhead / bird's-eye",
              "Camera directly above — flattens geography into a diagram; reads as fate, surveillance, or pattern.",
              supports_intent=("disorient", "observe")),
    Technique("ground_level", "angle", "Ground level",
              "Camera at or near ground height — makes ordinary action feel monumental or threatening.",
              supports_intent=("dominate", "disorient")),
    Technique("dutch", "angle", "Dutch / canted angle",
              "Camera tilted off the horizontal — reads as instability, unease, or disorientation.",
              supports_intent=("disorient",), conflicts_with=("eye_level",)),
    Technique("pov", "angle", "Point of view",
              "Camera stands in for a character's own eyes — collapses the distance between audience and subject.",
              supports_intent=("intimate", "disorient")),
    Technique("profile", "angle", "Profile / side-on",
              "Subject shot from the side — withholds direct engagement, often reads as contemplative or guarded.",
              supports_intent=("conceal", "observe")),

    # --- Camera movement ----------------------------------------------------
    Technique("static", "movement", "Static / locked-off",
              "No camera movement — lets performance and composition carry the shot without added energy.",
              supports_intent=("observe", "pause"), conflicts_with=("handheld",)),
    Technique("push_in", "movement", "Push-in / dolly-in",
              "Camera moves toward the subject — builds tension or focuses attention as it tightens the frame.",
              supports_intent=("reveal", "intimate"), requires=("sufficient_duration",)),
    Technique("pull_out", "movement", "Pull-out / dolly-out",
              "Camera moves away from the subject — reveals context, isolates, or releases tension.",
              supports_intent=("reveal", "release", "isolate"), requires=("sufficient_duration",)),
    Technique("pan", "movement", "Pan",
              "Camera rotates horizontally from a fixed point — follows action or reveals what's beside the subject.",
              supports_intent=("reveal", "observe")),
    Technique("tilt", "movement", "Tilt",
              "Camera rotates vertically from a fixed point — reveals height, scale, or a vertical relationship.",
              supports_intent=("reveal", "dominate")),
    Technique("track", "movement", "Track / follow",
              "Camera moves alongside or behind a moving subject — sustains proximity through motion.",
              supports_intent=("pursue", "observe"), requires=("sufficient_duration",)),
    Technique("arc", "movement", "Arc / orbit",
              "Camera moves in a curve around the subject — reveals dimensionality without cutting.",
              supports_intent=("reveal", "dominate"), requires=("sufficient_duration", "spatial_depth")),
    Technique("crane", "movement", "Crane / jib",
              "Camera moves vertically, often combined with a push or pull — grand scale changes within one shot.",
              supports_intent=("establish", "release"), requires=("sufficient_duration",)),
    Technique("handheld", "movement", "Handheld",
              "Camera carried, not stabilized — reads as urgency, chaos, or documentary immediacy.",
              supports_intent=("disorient", "pursue"), conflicts_with=("static",)),
    Technique("dolly_zoom", "movement", "Dolly zoom",
              "Camera moves while the lens zooms the opposite direction — background warps while the subject stays framed; a strong, rare effect.",
              supports_intent=("disorient", "reveal"), requires=("spatial_depth", "stable_subject")),

    # --- Composition -----------------------------------------------------
    Technique("centered", "composition", "Centered",
              "Subject placed in the frame's center — reads as symmetry, confrontation, or formal stillness.",
              supports_intent=("dominate", "observe")),
    Technique("thirds", "composition", "Rule of thirds",
              "Subject placed off-center on a third-line — the conventional, comfortably dynamic default.",
              supports_intent=("observe",)),
    Technique("negative_space", "composition", "Negative space",
              "Subject occupies a small part of the frame, surrounded by empty space — reads as isolation or smallness.",
              supports_intent=("isolate",), pairs_with=("wide",)),
    Technique("leading_lines", "composition", "Leading lines",
              "Environmental lines (a road, a hallway, a rail) draw the eye toward the subject.",
              supports_intent=("reveal", "establish")),
    Technique("frame_within_frame", "composition", "Frame within frame",
              "A doorway, window, or other environmental element frames the subject inside the frame.",
              supports_intent=("conceal", "observe")),
    Technique("depth_layers", "composition", "Foreground/background depth layers",
              "Distinct foreground, midground and background elements build spatial depth in one composition.",
              supports_intent=("establish", "reveal")),
    Technique("short_side", "composition", "Short-siding",
              "Subject looks/faces away from the larger side of the frame — creates unease or anticipation.",
              supports_intent=("disorient", "pursue")),
    Technique("dirty_frame", "composition", "Dirty frame",
              "An out-of-focus foreground element partially obscures the shot — adds voyeurism or immediacy.",
              supports_intent=("conceal", "disorient")),

    # --- Focus / lens -----------------------------------------------------
    Technique("deep_focus", "focus", "Deep focus",
              "Foreground through background all in focus — lets the audience choose where to look.",
              supports_intent=("establish", "observe"), conflicts_with=("shallow_focus",)),
    Technique("shallow_focus", "focus", "Shallow focus",
              "A narrow plane in focus, everything else soft — directs attention precisely.",
              supports_intent=("intimate", "isolate"), conflicts_with=("deep_focus", "depth_layers")),
    Technique("rack_focus", "focus", "Rack focus",
              "Focus shifts from one plane to another within the shot — redirects attention without a cut.",
              supports_intent=("reveal",), requires=("sufficient_duration",)),
    Technique("wide_lens", "focus", "Wide lens intent",
              "Short focal length — exaggerates depth and space, distorts close subjects.",
              supports_intent=("establish", "disorient")),
    Technique("normal_lens", "focus", "Normal lens intent",
              "Focal length near natural human perspective — a neutral default with no added distortion.",
              supports_intent=("observe",)),
    Technique("portrait_lens", "focus", "Portrait lens intent",
              "Medium-long focal length — flattering compression, the standard close-up/dialogue choice.",
              supports_intent=("intimate",)),
    Technique("telephoto_lens", "focus", "Telephoto lens intent",
              "Long focal length — heavy compression, isolates a subject from a distance.",
              supports_intent=("isolate", "pursue"), pairs_with=("compression",)),
    Technique("compression", "focus", "Lens compression",
              "Background appears closer to and larger relative to the subject — flattens depth.",
              supports_intent=("isolate",), pairs_with=("telephoto_lens",)),

    # --- Lighting -----------------------------------------------------
    Technique("high_key", "lighting", "High-key lighting",
              "Bright, low-contrast lighting with soft or no shadows — reads as safe, ordinary, or optimistic.",
              supports_intent=("establish", "observe"), conflicts_with=("low_key",)),
    Technique("low_key", "lighting", "Low-key lighting",
              "Dark, high-contrast lighting with deep shadows — reads as threat, mystery, or intimacy.",
              supports_intent=("conceal", "intimate", "disorient"), conflicts_with=("high_key",)),
    Technique("hard_light", "lighting", "Hard light",
              "A small or distant source casts sharp, defined shadows — reads as harsh, dramatic, or exposed.",
              supports_intent=("dominate", "reveal")),
    Technique("soft_light", "lighting", "Soft light",
              "A large or diffused source casts gentle, gradual shadows — reads as flattering or gentle.",
              supports_intent=("intimate",)),
    Technique("motivated", "lighting", "Motivated lighting",
              "Light sourced from a visible in-scene origin (a window, a lamp) — reads as grounded and real.",
              supports_intent=("establish", "observe")),
    Technique("practical", "lighting", "Practical source",
              "A visible fixture (lamp, candle, screen) is itself the light source in frame.",
              supports_intent=("intimate", "establish")),
    Technique("side_light", "lighting", "Side light",
              "Light from 90 degrees to the subject — carves form, half the face in shadow.",
              supports_intent=("conceal", "reveal")),
    Technique("back_light", "lighting", "Back light / rim light",
              "Light from behind the subject — separates them from the background with a rim of light.",
              supports_intent=("reveal", "establish")),
    Technique("window_light", "lighting", "Window-side light",
              "Soft, directional light motivated by a window — a common naturalistic interior choice.",
              supports_intent=("intimate", "observe"), pairs_with=("soft_light", "motivated")),
    Technique("silhouette", "lighting", "Silhouette",
              "Subject lit only from behind, their own form left dark — conceals identity/expression entirely.",
              supports_intent=("conceal", "isolate"), conflicts_with=("high_key",)),
    Technique("volumetric", "lighting", "Volumetric / atmospheric light",
              "Light rendered visible through haze, dust or fog — adds mood and depth cues.",
              supports_intent=("establish", "disorient")),

    # --- Edit relation (how this shot meets its neighbor) ------------------
    Technique("cut", "edit_relation", "Cut",
              "An instantaneous change to a new shot — the default, invisible when motivated.",
              supports_intent=("observe",)),
    Technique("match_on_action", "edit_relation", "Match on action",
              "A cut made mid-movement so the action continues seamlessly across the cut.",
              supports_intent=("observe", "accelerate")),
    Technique("reaction_cut", "edit_relation", "Reaction cut",
              "Cuts to a character's response immediately after the triggering action.",
              supports_intent=("intimate", "reveal"), pairs_with=("reaction",)),
    Technique("insert_cut", "edit_relation", "Insert cut",
              "Cuts briefly to a tight detail, then back to the main coverage.",
              supports_intent=("reveal", "isolate"), pairs_with=("insert",)),
    Technique("continuous_movement", "edit_relation", "Continuous movement",
              "The next shot picks up the same physical motion without a hard break in time or action.",
              supports_intent=("accelerate", "pursue")),
    Technique("ellipsis", "edit_relation", "Ellipsis",
              "The cut skips forward in time, omitting the interval between shots.",
              supports_intent=("accelerate", "pause")),
    Technique("j_cut", "edit_relation", "J-cut",
              "The next shot's audio begins before its picture — leads the audience into the cut.",
              supports_intent=("reveal", "accelerate")),
    Technique("l_cut", "edit_relation", "L-cut",
              "The current shot's audio continues after its picture has cut away — lingers a beat.",
              supports_intent=("observe", "pause")),
)

TECHNIQUES: dict[str, Technique] = {t.id: t for t in _TECHNIQUES}

CATEGORIES: tuple[str, ...] = (
    "shot_scale", "angle", "movement", "composition", "focus", "lighting", "edit_relation",
)


def get_technique(technique_id: str) -> Technique | None:
    return TECHNIQUES.get(technique_id)


def techniques_by_category(category: str) -> list[Technique]:
    return [t for t in _TECHNIQUES if t.category == category]


def techniques_for_intent(intent: str) -> list[Technique]:
    """Every technique that can express *intent*, across all categories."""
    return [t for t in _TECHNIQUES if intent in t.supports_intent]


def check_conflicts(technique_ids: list[str]) -> list[tuple[str, str]]:
    """Pairs of ids in *technique_ids* that conflict with each other.

    Symmetric by construction (each pair is checked from both sides, since
    conflicts_with is not always authored on both techniques), so a caller
    gets every real conflict regardless of which technique declared it.
    Unknown ids are ignored here rather than raised — callers that need
    strict validation should check membership in TECHNIQUES separately.
    """
    chosen = set(technique_ids)
    found: list[tuple[str, str]] = []
    seen: set[frozenset] = set()
    for tid in technique_ids:
        technique = TECHNIQUES.get(tid)
        if technique is None:
            continue
        for other in technique.conflicts_with:
            if other in chosen:
                pair = frozenset((tid, other))
                if pair not in seen:
                    seen.add(pair)
                    found.append(tuple(sorted((tid, other))))
    return found


def cinematic_spec_flags(shot: Shot) -> list[ContinuityFlag]:
    """Flag unknown or conflicting technique ids on a shot's cinematic_spec.

    A lint, matching moviecrew.rules.generative_video_flags: reads what the
    Cinematographer chose and warns, never constrains or rejects a shot
    outright — a technique id typo and a deliberate creative conflict (e.g.
    handheld + a locked-off static frame) both deserve human review, not an
    automatic rejection this layer has no authority to make.
    """
    spec = shot.cinematic_spec
    if spec is None or not spec.technique_ids:
        return []
    flags: list[ContinuityFlag] = []
    unknown = sorted(tid for tid in spec.technique_ids if tid not in TECHNIQUES)
    if unknown:
        flags.append(ContinuityFlag(
            target=shot.id, kind="warning",
            message=f"cinematic_spec references unknown technique id(s): {unknown}",
        ))
    for a, b in check_conflicts(spec.technique_ids):
        flags.append(ContinuityFlag(
            target=shot.id, kind="warning",
            message=f"cinematic_spec combines conflicting techniques: {a!r} and {b!r}",
        ))
    return flags


def compile_cinematic_spec_summary(spec: CinematicSpec) -> str:
    """A compact, resolved phrase for a shot's cinematic_spec.

    This is the "provider compiler" step in miniature: it resolves technique
    ids to real cinematography language via TECHNIQUES so a downstream
    prompt writer (the Prompter agent) never has to interpret a raw id like
    'push_in' itself, and never sees the rationale — only the render-
    relevant result. Provider-specific control-field compilation (Phase 2's
    fuller scope) is not attempted here; every current provider takes prose,
    not structured camera fields, so prose is the only compilation target
    that means anything today.
    """
    def resolved(technique_id: str) -> str:
        technique = TECHNIQUES.get(technique_id)
        return technique.name.lower() if technique else technique_id.replace("_", " ")

    parts: list[str] = []
    cam = spec.camera
    if cam.movement_type:
        bits = [resolved(cam.movement_type)]
        if cam.movement_speed:
            bits.append(cam.movement_speed)
        if cam.movement_motivation:
            bits.append(f"({cam.movement_motivation})")
        parts.append(" ".join(bits))
    if cam.shot_scale_start or cam.shot_scale_end:
        if cam.shot_scale_start and cam.shot_scale_end and cam.shot_scale_start != cam.shot_scale_end:
            parts.append(f"{resolved(cam.shot_scale_start)} to {resolved(cam.shot_scale_end)}")
        else:
            parts.append(resolved(cam.shot_scale_start or cam.shot_scale_end))
    if cam.angle:
        parts.append(resolved(cam.angle))
    if cam.lens_mm:
        parts.append(f"{cam.lens_mm}mm")

    if spec.focus.mode == "rack" and spec.focus.rack_from and spec.focus.rack_to:
        parts.append(f"rack focus {spec.focus.rack_from} to {spec.focus.rack_to}")
    elif spec.focus.mode:
        parts.append(f"{spec.focus.mode} focus")

    parts.extend(resolved(tid) for tid in spec.composition.techniques)

    if spec.lighting.key:
        parts.append(resolved(spec.lighting.key) if spec.lighting.key in TECHNIQUES else spec.lighting.key.replace("_", " "))

    summary = "; ".join(p for p in parts if p)
    if spec.narrative_intents:
        summary += f". Intent: {', '.join(spec.narrative_intents)}"
    return summary
