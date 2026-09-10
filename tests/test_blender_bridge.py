"""Tests for the Blender add-on's bridge layer, without Blender.

`bridge.py` deliberately has no top-level `import bpy` — the functions that
touch datablocks take them as arguments. That keeps project parsing and the
rendered-file normalisation testable here, which matters because those are
the parts most likely to be wrong and the hardest to debug from inside
Blender.

The module is loaded by path so the package's `__init__` (which does import
bpy) never runs.
"""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pytest

_BRIDGE_PATH = (
    Path(__file__).resolve().parents[1] / "blender" / "moviecrew_blender" / "bridge.py"
)


@pytest.fixture()
def bridge():
    """A freshly loaded bridge module, so global PROJECT state never leaks."""
    spec = importlib.util.spec_from_file_location("_mc_bridge", _BRIDGE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _project(**overrides) -> dict:
    data = {
        "title": "The Last Lighthouse",
        "scenes": [
            {
                "id": "sc1",
                "title": "Arrival",
                "summary": "Mara climbs the cliff path.",
                "shots": [
                    {
                        "id": "sc1-sh1",
                        "description": "Wide shot of the climb.",
                        "duration_s": 8,
                        "camera_move": "slow dolly-in",
                        "lens": "24mm",
                        "framing": "wide, low angle",
                    },
                    {
                        "id": "sc1-sh2",
                        "description": "Her hand on the door.",
                        "duration_s": 4,
                        "camera_move": "static",
                        "lens": "85mm",
                        "framing": "close-up",
                    },
                ],
            },
            {"id": "sc2", "title": "The Bargain", "summary": "", "shots": []},
        ],
    }
    data.update(overrides)
    return data


def _write_project(tmp_path: Path, data: dict) -> str:
    path = tmp_path / "project.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return str(path)


# ---------------------------------------------------------------------- #
# load_project                                                            #
# ---------------------------------------------------------------------- #


def test_load_project_reads_scenes(bridge, tmp_path):
    assert bridge.load_project(_write_project(tmp_path, _project())) is None
    assert bridge.PROJECT["title"] == "The Last Lighthouse"
    assert len(bridge.scenes()) == 2


def test_load_project_reports_a_missing_file(bridge, tmp_path):
    error = bridge.load_project(str(tmp_path / "nope.json"))
    assert error and "No project file" in error


def test_load_project_reports_malformed_json(bridge, tmp_path):
    path = tmp_path / "project.json"
    path.write_text("{ not json", encoding="utf-8")
    error = bridge.load_project(str(path))
    assert error and "Could not read" in error


def test_load_project_rejects_a_file_with_no_scenes(bridge, tmp_path):
    error = bridge.load_project(_write_project(tmp_path, _project(scenes=[])))
    assert error and "no scenes" in error


def test_failed_load_leaves_previous_project_intact(bridge, tmp_path):
    bridge.load_project(_write_project(tmp_path, _project()))
    bridge.load_project(str(tmp_path / "missing.json"))
    assert bridge.PROJECT["title"] == "The Last Lighthouse"


# ---------------------------------------------------------------------- #
# Lookups                                                                 #
# ---------------------------------------------------------------------- #


def test_shots_in_returns_only_that_scenes_shots(bridge, tmp_path):
    bridge.load_project(_write_project(tmp_path, _project()))
    assert [s["id"] for s in bridge.shots_in("sc1")] == ["sc1-sh1", "sc1-sh2"]
    assert bridge.shots_in("sc2") == []


def test_shots_in_unknown_scene_is_empty_not_an_error(bridge, tmp_path):
    bridge.load_project(_write_project(tmp_path, _project()))
    assert bridge.shots_in("nope") == []


def test_find_shot_locates_within_its_scene(bridge, tmp_path):
    bridge.load_project(_write_project(tmp_path, _project()))
    assert bridge.find_shot("sc1", "sc1-sh2")["lens"] == "85mm"


def test_find_shot_returns_none_for_wrong_scene(bridge, tmp_path):
    bridge.load_project(_write_project(tmp_path, _project()))
    assert bridge.find_shot("sc2", "sc1-sh1") is None


def test_lookups_are_safe_before_any_project_is_loaded(bridge):
    assert bridge.scenes() == []
    assert bridge.shots_in("sc1") == []
    assert bridge.find_shot("sc1", "sc1-sh1") is None


# ---------------------------------------------------------------------- #
# Shot adaptation + blocking                                              #
# ---------------------------------------------------------------------- #


def test_shot_view_exposes_what_blocking_needs(bridge):
    view = bridge._ShotView(
        {"id": "sc1-sh1", "duration_s": 8, "camera_move": "pan left", "lens": "24mm", "framing": "wide"}
    )
    assert (view.id, view.duration_s, view.lens) == ("sc1-sh1", 8, "24mm")


def test_shot_view_tolerates_missing_keys(bridge):
    view = bridge._ShotView({"id": "x"})
    assert view.camera_move == "" and view.duration_s == 0


def test_block_for_produces_blocking_from_a_raw_dict(bridge, tmp_path):
    bridge.load_project(_write_project(tmp_path, _project()))
    blocking = bridge.block_for(bridge.find_shot("sc1", "sc1-sh1"), fps=24)
    assert blocking.shot_id == "sc1-sh1"
    assert blocking.frame_end == 192  # 8s at 24fps
    assert blocking.is_animated  # it's a dolly-in


# ---------------------------------------------------------------------- #
# claim_rendered_file                                                     #
# ---------------------------------------------------------------------- #


def test_claim_renames_blenders_frame_range_output(bridge, tmp_path):
    """Blender decorates a movie path with the frame range; the take record
    points at the undecorated name, so whatever landed gets renamed."""
    (tmp_path / "take_0010001-0000192.mp4").write_bytes(b"MP4")
    destination = tmp_path / "take_001.mp4"

    assert bridge.claim_rendered_file(tmp_path, "take_001", destination) == destination
    assert destination.is_file()
    assert not (tmp_path / "take_0010001-0000192.mp4").exists()


def test_claim_is_a_no_op_when_blender_wrote_the_exact_name(bridge, tmp_path):
    destination = tmp_path / "take_001.mp4"
    destination.write_bytes(b"MP4")

    assert bridge.claim_rendered_file(tmp_path, "take_001", destination) == destination
    assert destination.read_bytes() == b"MP4"


def test_claim_returns_none_when_nothing_was_rendered(bridge, tmp_path):
    assert bridge.claim_rendered_file(tmp_path, "take_001", tmp_path / "take_001.mp4") is None


def test_claim_ignores_other_takes(bridge, tmp_path):
    (tmp_path / "take_0020001-0000192.mp4").write_bytes(b"OTHER")
    assert bridge.claim_rendered_file(tmp_path, "take_001", tmp_path / "take_001.mp4") is None


def test_claim_ignores_non_video_siblings(bridge, tmp_path):
    (tmp_path / "take_001.json").write_text("{}", encoding="utf-8")
    assert bridge.claim_rendered_file(tmp_path, "take_001", tmp_path / "take_001.mp4") is None


def test_claim_picks_the_newest_when_several_match(bridge, tmp_path):
    import os
    import time

    old = tmp_path / "take_0010001-0000100.mp4"
    old.write_bytes(b"OLD")
    os.utime(old, (time.time() - 600, time.time() - 600))
    new = tmp_path / "take_0010001-0000192.mp4"
    new.write_bytes(b"NEW")

    destination = tmp_path / "take_001.mp4"
    bridge.claim_rendered_file(tmp_path, "take_001", destination)
    assert destination.read_bytes() == b"NEW"


def test_claim_handles_alternative_containers(bridge, tmp_path):
    (tmp_path / "take_0010001-0000192.mkv").write_bytes(b"MKV")
    destination = tmp_path / "take_001.mp4"
    assert bridge.claim_rendered_file(tmp_path, "take_001", destination) == destination


# ---------------------------------------------------------------------- #
# ensure_moviecrew_importable                                             #
# ---------------------------------------------------------------------- #


def test_ensure_importable_succeeds_when_already_on_path(bridge):
    """moviecrew is importable in this test run, so no path is needed."""
    assert bridge.ensure_moviecrew_importable("") is None


def test_ensure_importable_error_names_the_preference(bridge, monkeypatch):
    monkeypatch.setitem(__import__("sys").modules, "moviecrew", None)
    error = bridge.ensure_moviecrew_importable("/nonexistent/path")
    if error is not None:  # only asserts when the import genuinely failed
        assert "Preferences" in error


# ---------------------------------------------------------------------- #
# Icon safety                                                             #
# ---------------------------------------------------------------------- #

_ADDON_DIR = _BRIDGE_PATH.parent


def test_every_icon_goes_through_the_guard():
    """A wrong icon name raises TypeError inside draw(), which aborts the
    whole panel — every control after the bad row vanishes with no visible
    cause. `_icon()` degrades that to a missing icon, so nothing may pass an
    icon literal directly.

    Regression: `CON_CAMERASOLVE` (the real enum is `CON_CAMERASOLVER`)
    silently blanked the sidebar below the shot summary.
    """
    offenders = []
    for path in sorted(_ADDON_DIR.glob("*.py")):
        for number, line in enumerate(path.read_text().splitlines(), 1):
            if re.search(r'icon="[A-Z0-9_]+"', line):
                offenders.append(f"{path.name}:{number}: {line.strip()}")
    assert not offenders, "icon literals must be wrapped in _icon():\n" + "\n".join(
        offenders
    )


# ---------------------------------------------------------------------- #
# configure_video_render — Blender 4.x vs 5.x                             #
# ---------------------------------------------------------------------- #


class _FakeImageSettings:
    """Mimics ImageFormatSettings, including Blender 5's ordering rule.

    In Blender 5.0 `file_format` lists still-image formats only; FFMPEG is
    reachable just once `media_type` is VIDEO. Assigning it too early raises
    TypeError, exactly as Blender does.
    """

    def __init__(self, *, has_media_type: bool):
        object.__setattr__(self, "has_media_type", has_media_type)
        object.__setattr__(self, "log", [])
        if has_media_type:
            object.__setattr__(self, "media_type", "IMAGE")
        object.__setattr__(self, "file_format", "PNG")

    def __setattr__(self, name, value):
        if (
            name == "file_format"
            and value == "FFMPEG"
            and self.has_media_type
            and getattr(self, "media_type", None) != "VIDEO"
        ):
            raise TypeError(
                'bpy_struct: item.attr = val: enum "FFMPEG" not found in '
                "('AVIF', 'JPEG', 'PNG', ...)"
            )
        self.log.append(name)
        object.__setattr__(self, name, value)


class _FakeScene:
    def __init__(self, *, has_media_type: bool):
        self.frame_start = 0
        self.frame_end = 0
        self.render = type(
            "R",
            (),
            {
                "image_settings": _FakeImageSettings(has_media_type=has_media_type),
                "ffmpeg": type("F", (), {})(),
                "fps": 0,
                "filepath": "",
            },
        )()


def _blocking(bridge, tmp_path):
    from moviecrew.blocking import block_shot

    return block_shot(bridge._ShotView({"id": "s1", "duration_s": 8}), fps=24)


def test_configure_video_render_sets_media_type_before_format_on_blender_5(
    bridge, tmp_path
):
    """Regression: Blender 5.0 rejects FFMPEG until media_type is VIDEO."""
    scene = _FakeScene(has_media_type=True)
    bridge.configure_video_render(scene, str(tmp_path / "take_001"), _blocking(bridge, tmp_path))

    settings = scene.render.image_settings
    assert settings.media_type == "VIDEO"
    assert settings.file_format == "FFMPEG"
    assert settings.log.index("media_type") < settings.log.index("file_format")


def test_configure_video_render_still_works_on_blender_4(bridge, tmp_path):
    """Older Blender has no media_type and takes FFMPEG directly."""
    scene = _FakeScene(has_media_type=False)
    bridge.configure_video_render(scene, str(tmp_path / "take_001"), _blocking(bridge, tmp_path))

    settings = scene.render.image_settings
    assert settings.file_format == "FFMPEG"
    assert not hasattr(settings, "media_type")


def test_configure_video_render_carries_the_frame_range(bridge, tmp_path):
    scene = _FakeScene(has_media_type=True)
    blocking = _blocking(bridge, tmp_path)
    bridge.configure_video_render(scene, str(tmp_path / "take_001"), blocking)

    assert (scene.frame_start, scene.frame_end) == (1, 192)
    assert scene.render.fps == 24
