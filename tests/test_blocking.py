"""Tests for prose-to-camera blocking.

Fully offline and Blender-free: `blocking` computes plain numbers, so the
parsing and the geometry are testable without bpy anywhere in the loop.
"""

from __future__ import annotations

import math

import pytest

from moviecrew.blocking import (
    DEFAULT_DISTANCE_M,
    DEFAULT_FPS,
    DEFAULT_LENS_MM,
    MOVE_CRANE_UP,
    MOVE_DOLLY_IN,
    MOVE_DOLLY_OUT,
    MOVE_ORBIT_LEFT,
    MOVE_PAN_LEFT,
    MOVE_STATIC,
    MOVE_TILT_DOWN,
    MOVE_TILT_UP,
    MOVE_TRACK_RIGHT,
    MOVE_ZOOM_IN,
    MOVE_ZOOM_OUT,
    block_shot,
    look_at_rotation,
    parse_framing,
    parse_lens_mm,
    parse_move,
)
from moviecrew.schema import Shot


def _shot(**overrides) -> Shot:
    defaults = dict(
        id="sc1-sh1",
        scene_id="sc1",
        description="Mara climbs the cliff path.",
        duration_s=8,
        camera_move="static",
        lens="50mm",
        framing="medium",
    )
    defaults.update(overrides)
    return Shot(**defaults)


# ---------------------------------------------------------------------- #
# Lens                                                                    #
# ---------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "text,expected",
    [("24mm", 24.0), ("85 mm", 85.0), ("shot on a 14mm", 14.0), ("35.5mm", 35.5)],
)
def test_parse_lens_reads_focal_length(text, expected):
    assert parse_lens_mm(text) == expected


def test_parse_lens_falls_back_to_normal_lens():
    assert parse_lens_mm("anamorphic something") == DEFAULT_LENS_MM


def test_parse_lens_notes_the_fallback():
    notes: list[str] = []
    parse_lens_mm("wide glass", notes)
    assert notes and "not understood" in notes[0]


def test_parse_lens_notes_when_nothing_was_given():
    notes: list[str] = []
    parse_lens_mm("", notes)
    assert notes and "no lens given" in notes[0]


def test_parse_lens_adds_no_note_when_understood():
    notes: list[str] = []
    parse_lens_mm("24mm", notes)
    assert notes == []


# ---------------------------------------------------------------------- #
# Framing                                                                 #
# ---------------------------------------------------------------------- #


def test_close_up_sits_nearer_than_wide():
    close, _ = parse_framing("close-up")
    wide, _ = parse_framing("wide")
    assert close < wide


def test_extreme_close_up_beats_close_up_despite_sharing_the_word():
    extreme, _ = parse_framing("extreme close-up")
    close, _ = parse_framing("close-up")
    assert extreme < close


def test_extreme_wide_beats_wide_despite_sharing_the_word():
    extreme, _ = parse_framing("extreme wide")
    wide, _ = parse_framing("wide")
    assert extreme > wide


def test_low_angle_drops_the_camera_below_high_angle():
    _, low = parse_framing("wide, low angle")
    _, high = parse_framing("wide, high angle")
    assert low < high


def test_framing_falls_back_to_a_default_distance():
    distance, _ = parse_framing("")
    assert distance == DEFAULT_DISTANCE_M


def test_framing_notes_the_fallback():
    notes: list[str] = []
    parse_framing("askew", notes)
    assert notes and "no shot size" in notes[0]


# ---------------------------------------------------------------------- #
# Move                                                                    #
# ---------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "text,expected",
    [
        ("static", MOVE_STATIC),
        ("locked off", MOVE_STATIC),
        ("slow dolly-in", MOVE_DOLLY_IN),
        ("dolly out", MOVE_DOLLY_OUT),
        ("push in", MOVE_DOLLY_IN),
        ("pull back", MOVE_DOLLY_OUT),
        ("pan left", MOVE_PAN_LEFT),
        ("tilt up", MOVE_TILT_UP),
        ("tilt down", MOVE_TILT_DOWN),
        ("crane up", MOVE_CRANE_UP),
        ("zoom in", MOVE_ZOOM_IN),
        ("zoom out", MOVE_ZOOM_OUT),
        ("orbit left", MOVE_ORBIT_LEFT),
        ("tracking shot", MOVE_TRACK_RIGHT),
    ],
)
def test_parse_move_recognises_common_phrasing(text, expected):
    kind, _ = parse_move(text)
    assert kind == expected


def test_dolly_out_is_not_swallowed_by_dolly_in():
    """Ordered longest-first, so the '-out' variant wins its own match."""
    assert parse_move("slow dolly-out")[0] == MOVE_DOLLY_OUT


def test_speed_words_scale_the_move():
    _, slow = parse_move("slow dolly-in")
    _, normal = parse_move("dolly-in")
    _, fast = parse_move("fast dolly-in")
    assert slow < normal < fast


def test_unknown_move_falls_back_to_static_with_a_note():
    notes: list[str] = []
    kind, _ = parse_move("vertigo rack whip-snap", notes)
    assert kind == MOVE_STATIC
    assert notes and "not understood" in notes[0]


# ---------------------------------------------------------------------- #
# look_at geometry                                                        #
# ---------------------------------------------------------------------- #


def test_camera_on_minus_y_needs_no_yaw():
    pitch, roll, yaw = look_at_rotation((0.0, -5.0, 1.7), (0.0, 0.0, 1.7))
    assert pitch == pytest.approx(math.pi / 2)
    assert roll == 0.0
    assert yaw == pytest.approx(0.0)


def test_camera_above_subject_pitches_down():
    pitch, _, _ = look_at_rotation((0.0, -5.0, 6.0), (0.0, 0.0, 1.7))
    assert pitch < math.pi / 2


def test_camera_below_subject_pitches_up():
    pitch, _, _ = look_at_rotation((0.0, -5.0, 0.3), (0.0, 0.0, 1.7))
    assert pitch > math.pi / 2


def test_camera_off_axis_yaws_a_quarter_turn_each_way():
    """Under yaw t the look direction is (-sin t, cos t): a camera on -X must
    look along +X, which is t = -pi/2, and +X is its mirror."""
    _, _, from_minus_x = look_at_rotation((-5.0, 0.0, 1.7), (0.0, 0.0, 1.7))
    _, _, from_plus_x = look_at_rotation((5.0, 0.0, 1.7), (0.0, 0.0, 1.7))
    assert from_minus_x == pytest.approx(-math.pi / 2)
    assert from_plus_x == pytest.approx(math.pi / 2)


# ---------------------------------------------------------------------- #
# block_shot                                                              #
# ---------------------------------------------------------------------- #


def test_block_shot_spans_the_duration_at_the_given_fps():
    blocking = block_shot(_shot(duration_s=8), fps=24)
    assert blocking.frame_start == 1
    assert blocking.frame_end == 192  # 8s * 24fps
    assert blocking.frame_count == 192


def test_block_shot_defaults_to_24fps():
    assert block_shot(_shot()).fps == DEFAULT_FPS


def test_block_shot_always_returns_two_keyframes():
    """Static shots key twice too, so callers need no special case."""
    assert len(block_shot(_shot(camera_move="static")).keyframes) == 2


def test_static_shot_is_not_animated():
    blocking = block_shot(_shot(camera_move="static"))
    assert not blocking.is_animated


def test_dolly_in_is_animated():
    assert block_shot(_shot(camera_move="slow dolly-in")).is_animated


def test_dolly_in_moves_the_camera_toward_the_subject():
    blocking = block_shot(_shot(camera_move="dolly-in", framing="medium"))
    start, end = blocking.keyframes
    assert abs(end.location[1]) < abs(start.location[1])


def test_dolly_out_moves_the_camera_away():
    blocking = block_shot(_shot(camera_move="dolly-out", framing="medium"))
    start, end = blocking.keyframes
    assert abs(end.location[1]) > abs(start.location[1])


def test_crane_up_raises_the_camera():
    blocking = block_shot(_shot(camera_move="crane up"))
    start, end = blocking.keyframes
    assert end.location[2] > start.location[2]


def test_track_right_slides_the_camera_sideways():
    blocking = block_shot(_shot(camera_move="track right"))
    start, end = blocking.keyframes
    assert end.location[0] > start.location[0]


def test_zoom_changes_focal_length_without_moving_the_camera():
    blocking = block_shot(_shot(camera_move="zoom in", lens="35mm"))
    start, end = blocking.keyframes
    assert end.location == start.location
    assert end.focal_length_mm > start.focal_length_mm


def test_dolly_keeps_focal_length_fixed():
    """A dolly is not a zoom — the lens must not change."""
    blocking = block_shot(_shot(camera_move="dolly-in", lens="35mm"))
    start, end = blocking.keyframes
    assert end.focal_length_mm == start.focal_length_mm == 35.0


def test_reframing_move_keeps_the_subject_centred():
    """A crane re-aims at the subject as it rises."""
    blocking = block_shot(_shot(camera_move="crane up"))
    start, end = blocking.keyframes
    assert end.rotation_euler != start.rotation_euler
    assert end.rotation_euler[0] < start.rotation_euler[0]  # now looking down


def test_pan_redirects_the_lens_without_moving_the_camera():
    blocking = block_shot(_shot(camera_move="pan left"))
    start, end = blocking.keyframes
    assert end.location == start.location
    assert end.rotation_euler[2] != start.rotation_euler[2]


def test_pan_left_and_right_turn_opposite_ways():
    left = block_shot(_shot(camera_move="pan left")).keyframes[1].rotation_euler[2]
    right = block_shot(_shot(camera_move="pan right")).keyframes[1].rotation_euler[2]
    assert left > right


def test_tilt_up_and_down_pitch_opposite_ways():
    up = block_shot(_shot(camera_move="tilt up")).keyframes[1].rotation_euler[0]
    down = block_shot(_shot(camera_move="tilt down")).keyframes[1].rotation_euler[0]
    assert up > down


def test_orbit_swings_the_camera_around_the_subject():
    blocking = block_shot(_shot(camera_move="orbit left", framing="medium"))
    start, end = blocking.keyframes
    assert end.location[0] != start.location[0]
    # Orbiting holds its distance from the subject.
    assert math.hypot(*start.location[:2]) == pytest.approx(
        math.hypot(*end.location[:2])
    )


def test_wide_shot_starts_further_back_than_close_up():
    wide = block_shot(_shot(framing="wide")).keyframes[0].location[1]
    close = block_shot(_shot(framing="close-up")).keyframes[0].location[1]
    assert abs(wide) > abs(close)


def test_lens_carries_onto_the_keyframes():
    blocking = block_shot(_shot(lens="24mm"))
    assert blocking.focal_length_mm == 24.0
    assert blocking.keyframes[0].focal_length_mm == 24.0


def test_notes_stay_empty_when_everything_parsed():
    blocking = block_shot(_shot(camera_move="dolly-in", lens="24mm", framing="wide"))
    assert blocking.notes == []


def test_notes_record_each_unparsed_field():
    """The gap between 'blocked as written' and 'defaulted' is what tells a
    caller where a human — or an LLM — needs to step in."""
    blocking = block_shot(_shot(camera_move="whip-snap", lens="???", framing="???"))
    assert len(blocking.notes) == 3


def test_block_shot_carries_the_shot_id():
    assert block_shot(_shot(id="sc2-sh4", scene_id="sc2")).shot_id == "sc2-sh4"


def test_crane_down_never_puts_the_camera_underground():
    blocking = block_shot(_shot(camera_move="fast crane down", framing="ground level"))
    assert blocking.keyframes[1].location[2] > 0
