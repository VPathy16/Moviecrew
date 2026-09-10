"""Turn a shot's written cinematography into camera keyframes.

The cinematographer agent already emits `camera_move`, `lens` and `framing`
as prose ("slow dolly-in", "24mm", "wide, low angle"). This module reads that
prose and produces a `CameraBlocking` — plain numbers describing where the
camera sits, where it points, and what it does over the shot's duration.

Nothing here imports `bpy`. Blender's add-on applies a CameraBlocking to a
real camera; this module computes it, so the parsing and the geometry stay
testable with no Blender in the loop — the same split `assembly.py` uses to
test its ffmpeg invocation without shelling out.

What it produces is a *starting block*, not a finished shot: a sane camera
that honours what the pipeline wrote, which an operator then adjusts by hand.
`CameraBlocking.notes` records every phrase that wasn't recognised, so the
caller can tell the difference between "blocked as written" and "fell back to
a default" — that gap is exactly where a human (or an LLM) should intervene.

Geometry convention (Blender's): +Z up, camera at rotation (pi/2, 0, 0) looks
along +Y. The subject stands at the origin; the camera starts on the -Y side
looking back at it.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Any, Optional

DEFAULT_LENS_MM = 50.0
DEFAULT_FPS = 24
DEFAULT_SUBJECT_HEIGHT_M = 1.7
DEFAULT_DISTANCE_M = 3.0
DEFAULT_CAMERA_HEIGHT_M = 1.6

# Speed words scale how far a move travels within the shot's fixed duration.
SPEED_SCALE: dict[str, float] = {"slow": 0.6, "fast": 1.6, "": 1.0}

# Framing -> how far back the camera sits, in metres.
FRAMING_DISTANCE_M: tuple[tuple[str, float], ...] = (
    ("extreme close-up", 0.6),
    ("extreme closeup", 0.6),
    ("extreme wide", 25.0),
    ("medium close-up", 2.0),
    ("medium closeup", 2.0),
    ("medium wide", 5.0),
    ("establishing", 25.0),
    ("close-up", 1.2),
    ("closeup", 1.2),
    ("medium", 3.0),
    ("wide", 9.0),
)

# Vertical phrasing -> camera height, in metres.
FRAMING_HEIGHT_M: tuple[tuple[str, float], ...] = (
    ("birds eye", 8.0),
    ("bird's eye", 8.0),
    ("overhead", 6.0),
    ("high angle", 3.2),
    ("low angle", 0.6),
    ("ground level", 0.15),
    ("eye level", 1.6),
)

# Move kinds.
MOVE_STATIC = "static"
MOVE_DOLLY_IN = "dolly_in"
MOVE_DOLLY_OUT = "dolly_out"
MOVE_TRACK_LEFT = "track_left"
MOVE_TRACK_RIGHT = "track_right"
MOVE_CRANE_UP = "crane_up"
MOVE_CRANE_DOWN = "crane_down"
MOVE_PAN_LEFT = "pan_left"
MOVE_PAN_RIGHT = "pan_right"
MOVE_TILT_UP = "tilt_up"
MOVE_TILT_DOWN = "tilt_down"
MOVE_ZOOM_IN = "zoom_in"
MOVE_ZOOM_OUT = "zoom_out"
MOVE_ORBIT_LEFT = "orbit_left"
MOVE_ORBIT_RIGHT = "orbit_right"

# Ordered longest-first so "dolly-out" never matches the "dolly" of "dolly-in".
_MOVE_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"dolly[\s-]*out", MOVE_DOLLY_OUT),
    (r"dolly[\s-]*in", MOVE_DOLLY_IN),
    (r"pull[\s-]*(out|back|away)", MOVE_DOLLY_OUT),
    (r"push[\s-]*(in|toward)", MOVE_DOLLY_IN),
    (r"zoom[\s-]*out", MOVE_ZOOM_OUT),
    (r"zoom[\s-]*in", MOVE_ZOOM_IN),
    (r"orbit[\s-]*left", MOVE_ORBIT_LEFT),
    (r"orbit[\s-]*right", MOVE_ORBIT_RIGHT),
    (r"(orbit|arc)", MOVE_ORBIT_LEFT),
    (r"crane[\s-]*(up|rise)", MOVE_CRANE_UP),
    (r"crane[\s-]*(down|descend)", MOVE_CRANE_DOWN),
    (r"(boom|jib)[\s-]*up", MOVE_CRANE_UP),
    (r"(boom|jib)[\s-]*down", MOVE_CRANE_DOWN),
    (r"tilt[\s-]*up", MOVE_TILT_UP),
    (r"tilt[\s-]*down", MOVE_TILT_DOWN),
    (r"pan[\s-]*left", MOVE_PAN_LEFT),
    (r"pan[\s-]*right", MOVE_PAN_RIGHT),
    (r"(track|truck|dolly)[\s-]*left", MOVE_TRACK_LEFT),
    (r"(track|truck|dolly)[\s-]*right", MOVE_TRACK_RIGHT),
    (r"(tracking|track|follow)", MOVE_TRACK_RIGHT),
    (r"(static|locked[\s-]*off|still|fixed|handheld)", MOVE_STATIC),
    (r"pan", MOVE_PAN_RIGHT),
    (r"tilt", MOVE_TILT_UP),
)

_LENS_RE = re.compile(r"(\d+(?:\.\d+)?)\s*mm", re.IGNORECASE)

# How far each move travels at speed 1.0.
_DOLLY_FRACTION = 0.35          # of the starting distance
_TRACK_METRES = 2.0
_CRANE_METRES = 1.8
_PAN_DEGREES = 20.0
_TILT_DEGREES = 12.0
_ZOOM_FACTOR = 0.8              # of the starting focal length
_ORBIT_DEGREES = 30.0

# Moves that re-aim at the subject as the camera travels; everything else
# redirects the lens away from it.
_REFRAMING_MOVES = frozenset(
    {
        MOVE_DOLLY_IN,
        MOVE_DOLLY_OUT,
        MOVE_TRACK_LEFT,
        MOVE_TRACK_RIGHT,
        MOVE_CRANE_UP,
        MOVE_CRANE_DOWN,
        MOVE_ORBIT_LEFT,
        MOVE_ORBIT_RIGHT,
        MOVE_ZOOM_IN,
        MOVE_ZOOM_OUT,
        MOVE_STATIC,
    }
)


@dataclass
class Keyframe:
    """One camera pose, in Blender's own units (metres, radians)."""

    frame: int
    location: tuple[float, float, float]
    rotation_euler: tuple[float, float, float]
    focal_length_mm: float


@dataclass
class CameraBlocking:
    shot_id: str
    keyframes: list[Keyframe]
    frame_start: int
    frame_end: int
    fps: int
    move: str
    focal_length_mm: float
    notes: list[str] = field(default_factory=list)

    @property
    def frame_count(self) -> int:
        return self.frame_end - self.frame_start + 1

    @property
    def is_animated(self) -> bool:
        """False when every keyframe holds the same pose (a locked-off shot)."""
        if len(self.keyframes) < 2:
            return False
        first = self.keyframes[0]
        return any(
            k.location != first.location
            or k.rotation_euler != first.rotation_euler
            or k.focal_length_mm != first.focal_length_mm
            for k in self.keyframes[1:]
        )


# --- Parsing ----------------------------------------------------------------


def parse_lens_mm(lens: str, notes: Optional[list[str]] = None) -> float:
    """``"24mm"`` -> ``24.0``. Falls back to a 50mm normal lens."""
    match = _LENS_RE.search(lens or "")
    if match:
        return float(match.group(1))
    if notes is not None and (lens or "").strip():
        notes.append(f"lens {lens!r} not understood; used {DEFAULT_LENS_MM:g}mm")
    elif notes is not None:
        notes.append(f"no lens given; used {DEFAULT_LENS_MM:g}mm")
    return DEFAULT_LENS_MM


def parse_framing(
    framing: str, notes: Optional[list[str]] = None
) -> tuple[float, float]:
    """``"wide, low angle"`` -> ``(distance_m, camera_height_m)``."""
    text = (framing or "").lower()

    distance = None
    for phrase, value in FRAMING_DISTANCE_M:
        if phrase in text:
            distance = value
            break

    height = None
    for phrase, value in FRAMING_HEIGHT_M:
        if phrase in text:
            height = value
            break

    if notes is not None and distance is None:
        notes.append(
            f"framing {framing!r} gave no shot size; used {DEFAULT_DISTANCE_M:g}m"
            if text.strip()
            else f"no framing given; used {DEFAULT_DISTANCE_M:g}m"
        )
    return (
        DEFAULT_DISTANCE_M if distance is None else distance,
        DEFAULT_CAMERA_HEIGHT_M if height is None else height,
    )


def parse_move(
    camera_move: str, notes: Optional[list[str]] = None
) -> tuple[str, float]:
    """``"slow dolly-in"`` -> ``("dolly_in", 0.6)``."""
    text = (camera_move or "").lower()

    speed = 1.0
    for word, scale in SPEED_SCALE.items():
        if word and word in text:
            speed = scale
            break

    for pattern, kind in _MOVE_PATTERNS:
        if re.search(pattern, text):
            return kind, speed

    if notes is not None:
        notes.append(
            f"camera move {camera_move!r} not understood; blocked as static"
            if text.strip()
            else "no camera move given; blocked as static"
        )
    return MOVE_STATIC, speed


# --- Geometry ---------------------------------------------------------------


def look_at_rotation(
    camera: tuple[float, float, float], target: tuple[float, float, float]
) -> tuple[float, float, float]:
    """Euler XYZ aiming a Blender camera at `target`.

    At rotation (pi/2, 0, 0) a Blender camera looks along +Y, so a camera on
    the -Y side of the subject needs no yaw.
    """
    dx = target[0] - camera[0]
    dy = target[1] - camera[1]
    dz = target[2] - camera[2]
    horizontal = math.hypot(dx, dy)
    pitch = math.pi / 2 + math.atan2(dz, horizontal)
    yaw = math.atan2(-dx, dy) if horizontal else 0.0
    return (pitch, 0.0, yaw)


def _end_pose(
    kind: str,
    speed: float,
    start: tuple[float, float, float],
    distance: float,
    lens_mm: float,
) -> tuple[tuple[float, float, float], float]:
    """Where the camera and its focal length end up."""
    x, y, z = start

    if kind == MOVE_DOLLY_IN:
        return (x, y + distance * _DOLLY_FRACTION * speed, z), lens_mm
    if kind == MOVE_DOLLY_OUT:
        return (x, y - distance * _DOLLY_FRACTION * speed, z), lens_mm
    if kind == MOVE_TRACK_LEFT:
        return (x - _TRACK_METRES * speed, y, z), lens_mm
    if kind == MOVE_TRACK_RIGHT:
        return (x + _TRACK_METRES * speed, y, z), lens_mm
    if kind == MOVE_CRANE_UP:
        return (x, y, z + _CRANE_METRES * speed), lens_mm
    if kind == MOVE_CRANE_DOWN:
        return (x, y, max(0.1, z - _CRANE_METRES * speed)), lens_mm
    if kind == MOVE_ZOOM_IN:
        return start, lens_mm * (1.0 + _ZOOM_FACTOR * speed)
    if kind == MOVE_ZOOM_OUT:
        return start, max(8.0, lens_mm / (1.0 + _ZOOM_FACTOR * speed))
    if kind in (MOVE_ORBIT_LEFT, MOVE_ORBIT_RIGHT):
        sign = -1.0 if kind == MOVE_ORBIT_LEFT else 1.0
        angle = math.radians(_ORBIT_DEGREES * speed) * sign
        # Rotate the camera around the subject's vertical axis.
        return (
            x * math.cos(angle) - y * math.sin(angle),
            x * math.sin(angle) + y * math.cos(angle),
            z,
        ), lens_mm
    return start, lens_mm


def _rotation_delta(kind: str, speed: float) -> tuple[float, float, float]:
    """Extra rotation for moves that redirect the lens off the subject."""
    if kind == MOVE_PAN_LEFT:
        return (0.0, 0.0, math.radians(_PAN_DEGREES * speed))
    if kind == MOVE_PAN_RIGHT:
        return (0.0, 0.0, -math.radians(_PAN_DEGREES * speed))
    if kind == MOVE_TILT_UP:
        return (math.radians(_TILT_DEGREES * speed), 0.0, 0.0)
    if kind == MOVE_TILT_DOWN:
        return (-math.radians(_TILT_DEGREES * speed), 0.0, 0.0)
    return (0.0, 0.0, 0.0)


# --- Blocking ---------------------------------------------------------------


def block_shot(
    shot: Any,
    *,
    fps: int = DEFAULT_FPS,
    frame_start: int = 1,
    subject_height_m: float = DEFAULT_SUBJECT_HEIGHT_M,
) -> CameraBlocking:
    """Block `shot`'s camera from its written cinematography.

    `shot` is duck-typed on schema.Shot — it needs `id`, `duration_s`, and the
    `camera_move` / `lens` / `framing` strings. Returns two keyframes (start
    and end pose); a static shot returns two identical ones so the caller can
    key it uniformly without special-casing.
    """
    notes: list[str] = []
    lens_mm = parse_lens_mm(getattr(shot, "lens", ""), notes)
    distance, height = parse_framing(getattr(shot, "framing", ""), notes)
    kind, speed = parse_move(getattr(shot, "camera_move", ""), notes)

    subject = (0.0, 0.0, subject_height_m)
    start_pos = (0.0, -distance, height)
    end_pos, end_lens = _end_pose(kind, speed, start_pos, distance, lens_mm)

    base_rotation = look_at_rotation(start_pos, subject)
    if kind in _REFRAMING_MOVES:
        end_rotation = look_at_rotation(end_pos, subject)
    else:
        delta = _rotation_delta(kind, speed)
        end_rotation = tuple(base + d for base, d in zip(base_rotation, delta))

    frame_count = max(1, round(float(getattr(shot, "duration_s", 0)) * fps))
    frame_end = frame_start + frame_count - 1

    return CameraBlocking(
        shot_id=getattr(shot, "id", ""),
        keyframes=[
            Keyframe(frame_start, start_pos, base_rotation, lens_mm),
            Keyframe(frame_end, end_pos, end_rotation, end_lens),
        ],
        frame_start=frame_start,
        frame_end=frame_end,
        fps=fps,
        move=kind,
        focal_length_mm=lens_mm,
        notes=notes,
    )
