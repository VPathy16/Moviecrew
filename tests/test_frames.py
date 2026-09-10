"""Tests for take frame extraction.

Offline: the ffmpeg command is asserted as data, and the subprocess call is
injected, so nothing shells out. Same split `test_assembly.py` uses.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from moviecrew.frames import (
    FIRST_FRAME_SUFFIX,
    LAST_FRAME_SUFFIX,
    build_extract_command,
    extract_bookend_frames,
    extract_frame,
)


class _Result:
    def __init__(self, returncode=0):
        self.returncode = returncode


def _runner(returncode=0, *, writes=True):
    """A fake subprocess.run that optionally creates the output file."""
    calls = []

    def run(cmd, **kwargs):
        calls.append(cmd)
        if writes and returncode == 0:
            Path(cmd[-1]).write_bytes(b"PNG")
        return _Result(returncode)

    run.calls = calls
    return run


@pytest.fixture()
def video(tmp_path) -> str:
    path = tmp_path / "take_001.mp4"
    path.write_bytes(b"\x00\x00\x00\x18ftypisom")
    return str(path)


# ---------------------------------------------------------------------- #
# Command building                                                        #
# ---------------------------------------------------------------------- #


def test_first_frame_command_does_not_seek():
    cmd = build_extract_command("in.mp4", "out.png")
    assert "-sseof" not in cmd
    assert cmd[:2] == ["ffmpeg", "-y"]
    assert cmd[-1] == "out.png"


def test_last_frame_command_seeks_from_the_end():
    """Seeking from the end needs no knowledge of duration or frame rate."""
    cmd = build_extract_command("in.mp4", "out.png", last=True)
    assert "-sseof" in cmd
    assert cmd[cmd.index("-sseof") + 1].startswith("-")


def test_command_extracts_exactly_one_frame():
    cmd = build_extract_command("in.mp4", "out.png")
    assert cmd[cmd.index("-frames:v") + 1] == "1"


def test_ffmpeg_binary_is_overridable():
    assert build_extract_command("i.mp4", "o.png", ffmpeg="/opt/ffmpeg")[0] == "/opt/ffmpeg"


# ---------------------------------------------------------------------- #
# extract_frame                                                           #
# ---------------------------------------------------------------------- #


def test_extract_writes_the_frame(video, tmp_path):
    out = str(tmp_path / "f.png")
    assert extract_frame(video, out, run=_runner()) == out
    assert Path(out).is_file()


def test_extract_creates_the_output_directory(video, tmp_path):
    out = str(tmp_path / "nested" / "deeper" / "f.png")
    assert extract_frame(video, out, run=_runner()) == out


def test_missing_video_returns_none_without_running_ffmpeg(tmp_path):
    run = _runner()
    assert extract_frame(str(tmp_path / "nope.mp4"), str(tmp_path / "f.png"), run=run) is None
    assert run.calls == []


def test_ffmpeg_failure_returns_none(video, tmp_path):
    assert extract_frame(video, str(tmp_path / "f.png"), run=_runner(1, writes=False)) is None


def test_missing_ffmpeg_returns_none_rather_than_raising(video, tmp_path):
    """A caller is mid-workflow with a take in hand and wants a reportable
    failure, not a traceback."""

    def explode(cmd, **kwargs):
        raise OSError("No such file or directory: 'ffmpeg'")

    assert extract_frame(video, str(tmp_path / "f.png"), run=explode) is None


def test_silent_success_that_wrote_nothing_returns_none(video, tmp_path):
    """ffmpeg can exit 0 having decoded no frame."""
    assert extract_frame(video, str(tmp_path / "f.png"), run=_runner(0, writes=False)) is None


# ---------------------------------------------------------------------- #
# extract_bookend_frames                                                  #
# ---------------------------------------------------------------------- #


def test_bookends_produce_two_distinct_files(video, tmp_path):
    first, last = extract_bookend_frames(video, str(tmp_path / "frames"), run=_runner())
    assert first and last and first != last
    assert first.endswith(FIRST_FRAME_SUFFIX)
    assert last.endswith(LAST_FRAME_SUFFIX)


def test_bookends_are_named_after_the_clip(video, tmp_path):
    first, _ = extract_bookend_frames(video, str(tmp_path / "frames"), run=_runner())
    assert Path(first).name == f"take_001{FIRST_FRAME_SUFFIX}"


def test_bookend_stem_is_overridable(video, tmp_path):
    first, _ = extract_bookend_frames(
        video, str(tmp_path / "frames"), stem="sc1-sh1-take1", run=_runner()
    )
    assert Path(first).name.startswith("sc1-sh1-take1")


def test_bookends_run_ffmpeg_twice(video, tmp_path):
    run = _runner()
    extract_bookend_frames(video, str(tmp_path / "frames"), run=run)
    assert len(run.calls) == 2
    assert ("-sseof" in run.calls[0]) != ("-sseof" in run.calls[1])


def test_bookends_report_failures_independently(video, tmp_path):
    """One frame failing must not discard the other."""
    calls = []

    def run(cmd, **kwargs):
        calls.append(cmd)
        if "-sseof" in cmd:  # fail only the last frame
            return _Result(1)
        Path(cmd[-1]).write_bytes(b"PNG")
        return _Result(0)

    first, last = extract_bookend_frames(video, str(tmp_path / "frames"), run=run)
    assert first is not None
    assert last is None


def test_bookends_of_a_missing_clip_are_both_none(tmp_path):
    first, last = extract_bookend_frames(
        str(tmp_path / "nope.mp4"), str(tmp_path / "frames"), run=_runner()
    )
    assert (first, last) == (None, None)
