"""Tests for the take library: path convention, records, and manifest.

Fully offline — takes are plain files under tmp_path; no video is ever
rendered, so a "clip" here is a few bytes standing in for an MP4.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from moviecrew.schema import Shot
from moviecrew.takes import (
    BLOCKED_BY_AUTO,
    BLOCKED_BY_LLM,
    BLOCKED_BY_MANUAL,
    MANIFEST_VERSION,
    Take,
    list_takes,
    load_manifest,
    load_take,
    manifest_path,
    new_take_for_shot,
    next_take_number,
    rebuild_manifest,
    resolve_video,
    save_take,
    scan_takes,
    shot_dir,
    take_record_path,
    take_stem,
    take_video_path,
)


def _take(**overrides) -> Take:
    defaults = dict(
        shot_id="sc1-sh1",
        scene_id="sc1",
        take_number=1,
        video_path="sc1/sc1-sh1/take_001.mp4",
    )
    defaults.update(overrides)
    return Take(**defaults)


# ---------------------------------------------------------------------- #
# Take dataclass                                                          #
# ---------------------------------------------------------------------- #


def test_take_id_is_shot_and_number():
    assert _take(take_number=2).take_id == "sc1-sh1#2"


def test_take_stamps_created_at_when_absent():
    assert _take().created_at  # ISO8601, filled in by __post_init__


def test_take_keeps_explicit_created_at():
    assert _take(created_at="2026-01-01T00:00:00+00:00").created_at == (
        "2026-01-01T00:00:00+00:00"
    )


def test_take_rejects_zero_or_negative_take_number():
    with pytest.raises(ValueError, match="take_number must be >= 1"):
        _take(take_number=0)


def test_take_rejects_unknown_blocking_mode():
    with pytest.raises(ValueError, match="blocked_by must be one of"):
        _take(blocked_by="telepathy")


def test_take_accepts_every_declared_blocking_mode():
    for mode in (BLOCKED_BY_MANUAL, BLOCKED_BY_AUTO, BLOCKED_BY_LLM):
        assert _take(blocked_by=mode).blocked_by == mode


def test_take_round_trips_through_to_dict_from_dict():
    original = _take(take_number=3, lens="85mm", media_id="m-1", renders=["r-1"])
    restored = Take.from_dict(original.to_dict())
    assert restored == original


def test_take_defaults_have_no_shared_mutable_state():
    a, b = _take(), _take()
    a.renders.append("r-1")
    assert b.renders == []


# ---------------------------------------------------------------------- #
# Path convention                                                         #
# ---------------------------------------------------------------------- #


def test_take_stem_zero_pads():
    assert take_stem(1) == "take_001"
    assert take_stem(42) == "take_042"


def test_take_paths_follow_scene_shot_convention(tmp_path):
    assert shot_dir(tmp_path, "sc1", "sc1-sh1") == tmp_path / "sc1" / "sc1-sh1"
    assert take_video_path(tmp_path, "sc1", "sc1-sh1", 2) == (
        tmp_path / "sc1" / "sc1-sh1" / "take_002.mp4"
    )
    assert take_record_path(tmp_path, "sc1", "sc1-sh1", 2) == (
        tmp_path / "sc1" / "sc1-sh1" / "take_002.json"
    )


def test_resolve_video_joins_relative_path_against_root(tmp_path):
    take = _take(video_path="sc1/sc1-sh1/take_001.mp4")
    assert resolve_video(take, tmp_path) == (
        tmp_path / "sc1" / "sc1-sh1" / "take_001.mp4"
    )


def test_resolve_video_keeps_absolute_path_unchanged(tmp_path):
    absolute = tmp_path / "elsewhere" / "clip.mp4"
    take = _take(video_path=str(absolute))
    assert resolve_video(take, tmp_path) == absolute


# ---------------------------------------------------------------------- #
# next_take_number                                                        #
# ---------------------------------------------------------------------- #


def test_next_take_number_starts_at_one_for_unknown_shot(tmp_path):
    assert next_take_number(tmp_path, "sc1", "sc1-sh1") == 1


def test_next_take_number_increments_past_existing_records(tmp_path):
    save_take(_take(take_number=1), tmp_path)
    save_take(_take(take_number=2, video_path="sc1/sc1-sh1/take_002.mp4"), tmp_path)
    assert next_take_number(tmp_path, "sc1", "sc1-sh1") == 3


def test_next_take_number_counts_orphan_clip_with_no_record(tmp_path):
    """A render that died before its record was written must not have its
    number reissued — the clip on disk still claims it."""
    directory = shot_dir(tmp_path, "sc1", "sc1-sh1")
    directory.mkdir(parents=True)
    (directory / "take_007.mp4").write_bytes(b"MP4")

    assert next_take_number(tmp_path, "sc1", "sc1-sh1") == 8


def test_next_take_number_is_per_shot(tmp_path):
    save_take(_take(take_number=1), tmp_path)
    assert next_take_number(tmp_path, "sc1", "sc1-sh2") == 1


# ---------------------------------------------------------------------- #
# save / load                                                             #
# ---------------------------------------------------------------------- #


def test_save_take_creates_directories_and_record(tmp_path):
    record = save_take(_take(), tmp_path)
    assert record == tmp_path / "sc1" / "sc1-sh1" / "take_001.json"
    assert record.is_file()


def test_save_take_round_trips_through_load_take(tmp_path):
    original = _take(take_number=2, lens="24mm", framing="wide", blocked_by=BLOCKED_BY_AUTO)
    save_take(original, tmp_path)
    assert load_take(tmp_path, "sc1", "sc1-sh1", 2) == original


def test_save_take_writes_manifest(tmp_path):
    save_take(_take(), tmp_path)
    assert manifest_path(tmp_path).is_file()


# ---------------------------------------------------------------------- #
# scan / list                                                             #
# ---------------------------------------------------------------------- #


def test_scan_takes_on_missing_root_returns_empty(tmp_path):
    assert scan_takes(tmp_path / "nope") == []


def test_scan_takes_sorts_by_scene_shot_then_number(tmp_path):
    save_take(_take(scene_id="sc2", shot_id="sc2-sh1"), tmp_path)
    save_take(_take(take_number=2), tmp_path)
    save_take(_take(take_number=1), tmp_path)

    found = [(t.scene_id, t.shot_id, t.take_number) for t in scan_takes(tmp_path)]
    assert found == [("sc1", "sc1-sh1", 1), ("sc1", "sc1-sh1", 2), ("sc2", "sc2-sh1", 1)]


def test_scan_takes_skips_malformed_record_without_losing_the_rest(tmp_path):
    save_take(_take(), tmp_path)
    broken = tmp_path / "sc1" / "sc1-sh1" / "take_009.json"
    broken.write_text("{ not json", encoding="utf-8")

    found = scan_takes(tmp_path)
    assert [t.take_number for t in found] == [1]


def test_list_takes_filters_by_shot(tmp_path):
    save_take(_take(), tmp_path)
    save_take(_take(shot_id="sc1-sh2", video_path="sc1/sc1-sh2/take_001.mp4"), tmp_path)

    assert [t.shot_id for t in list_takes(tmp_path, shot_id="sc1-sh2")] == ["sc1-sh2"]


def test_list_takes_filters_by_scene(tmp_path):
    save_take(_take(), tmp_path)
    save_take(_take(scene_id="sc2", shot_id="sc2-sh1"), tmp_path)

    assert [t.scene_id for t in list_takes(tmp_path, scene_id="sc2")] == ["sc2"]


# ---------------------------------------------------------------------- #
# Manifest                                                                #
# ---------------------------------------------------------------------- #


def test_load_manifest_returns_empty_shape_when_absent(tmp_path):
    manifest = load_manifest(tmp_path)
    assert manifest["take_count"] == 0
    assert manifest["shots"] == {}


def test_manifest_groups_takes_by_shot(tmp_path):
    save_take(_take(), tmp_path)
    save_take(_take(take_number=2, video_path="sc1/sc1-sh1/take_002.mp4"), tmp_path)
    save_take(_take(shot_id="sc1-sh2", video_path="sc1/sc1-sh2/take_001.mp4"), tmp_path)

    manifest = load_manifest(tmp_path)
    assert manifest["version"] == MANIFEST_VERSION
    assert manifest["take_count"] == 3
    assert len(manifest["shots"]["sc1-sh1"]) == 2
    assert len(manifest["shots"]["sc1-sh2"]) == 1


def test_rebuild_manifest_recovers_take_written_behind_its_back(tmp_path):
    """The sidecars are the source of truth: a record dropped in by hand (or
    by a Blender that died before reindexing) shows up after a rebuild."""
    save_take(_take(), tmp_path)

    directory = shot_dir(tmp_path, "sc1", "sc1-sh1")
    (directory / "take_005.json").write_text(
        json.dumps(_take(take_number=5, video_path="sc1/sc1-sh1/take_005.mp4").to_dict()),
        encoding="utf-8",
    )
    assert load_manifest(tmp_path)["take_count"] == 1  # stale

    rebuild_manifest(tmp_path)
    assert load_manifest(tmp_path)["take_count"] == 2


def test_rebuild_manifest_on_empty_root_creates_it(tmp_path):
    root = tmp_path / "takes"
    rebuild_manifest(root)
    assert load_manifest(root)["take_count"] == 0


# ---------------------------------------------------------------------- #
# new_take_for_shot                                                       #
# ---------------------------------------------------------------------- #


@pytest.fixture()
def shot() -> Shot:
    return Shot(
        id="sc1-sh1",
        scene_id="sc1",
        description="Mara climbs the cliff path.",
        duration_s=8,
        camera_move="slow dolly-in",
        lens="24mm",
        framing="wide, low angle",
    )


def test_new_take_for_shot_copies_the_cinematography(tmp_path, shot):
    take = new_take_for_shot(shot, "sc1", tmp_path)
    assert take.shot_id == "sc1-sh1"
    assert take.scene_id == "sc1"
    assert take.camera_move == "slow dolly-in"
    assert take.lens == "24mm"
    assert take.framing == "wide, low angle"
    assert take.duration_s == 8


def test_new_take_for_shot_starts_at_one_and_targets_the_convention(tmp_path, shot):
    take = new_take_for_shot(shot, "sc1", tmp_path)
    assert take.take_number == 1
    assert resolve_video(take, tmp_path) == take_video_path(tmp_path, "sc1", "sc1-sh1", 1)


def test_new_take_for_shot_increments_once_saved(tmp_path, shot):
    first = new_take_for_shot(shot, "sc1", tmp_path)
    save_take(first, tmp_path)

    assert new_take_for_shot(shot, "sc1", tmp_path).take_number == 2


def test_new_take_for_shot_records_blocking_mode(tmp_path, shot):
    take = new_take_for_shot(shot, "sc1", tmp_path, blocked_by=BLOCKED_BY_AUTO)
    assert take.blocked_by == BLOCKED_BY_AUTO


def test_new_take_for_shot_stores_a_relocatable_relative_path(tmp_path, shot):
    take = new_take_for_shot(shot, "sc1", tmp_path)
    assert not Path(take.video_path).is_absolute()
    assert take.video_path == str(Path("sc1") / "sc1-sh1" / "take_001.mp4")


def test_new_take_for_shot_returns_unsaved_take(tmp_path, shot):
    """The clip doesn't exist yet — the caller renders into it, then saves."""
    take = new_take_for_shot(shot, "sc1", tmp_path)
    assert not take_record_path(tmp_path, "sc1", "sc1-sh1", take.take_number).exists()
