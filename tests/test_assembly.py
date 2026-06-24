"""Tests for moviecrew.assembly, fully offline via an injected fake `run`."""

from __future__ import annotations

from moviecrew.assembly import assemble_film, build_concat_command
from moviecrew.schema import Bible, Project, RenderPlan
from moviecrew.video import RenderResult


class FakeRun:
    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    def __call__(self, command, *, check=False):
        self.calls.append(command)


def _project(chains: list[list[str]]) -> Project:
    return Project(
        title="t",
        logline="l",
        bible=Bible(style="s", palette="p", mood="m"),
        render_plan=RenderPlan(chains=chains),
    )


def _result(shot_id: str, *, status: str = "succeeded", uri: str | None = None) -> RenderResult:
    return RenderResult(shot_id=shot_id, status=status, backend="veo", uri=uri)


def test_build_concat_command_shape():
    cmd = build_concat_command(
        ["a.mp4", "b.mp4"], "out.mp4", ffmpeg="ffmpeg", target_resolution="720p", fps=24
    )

    assert cmd[0] == "ffmpeg"
    assert cmd[-1] == "out.mp4"
    assert "-i" in cmd and "a.mp4" in cmd and "b.mp4" in cmd
    filter_complex = cmd[cmd.index("-filter_complex") + 1]
    assert "scale=-2:720,fps=24" in filter_complex
    assert "[v0][0:a][v1][1:a]concat=n=2:v=1:a=1[outv][outa]" in filter_complex
    map_indices = [i for i, arg in enumerate(cmd) if arg == "-map"]
    assert [cmd[i + 1] for i in map_indices] == ["[outv]", "[outa]"]


def test_assemble_film_uses_chain_final_clip_in_chain_order():
    project = _project(chains=[["sc1-sh1"], ["sc2-sh1", "sc2-sh2"]])
    results = [
        _result("sc1-sh1", uri="renders/sc1-sh1.mp4"),
        _result("sc2-sh1", uri="renders/sc2-sh1.mp4"),
        _result("sc2-sh2", uri="renders/sc2-sh2.mp4"),
    ]
    run = FakeRun()

    out = assemble_film(project, results, "film.mp4", run=run)

    assert out == "film.mp4"
    assert len(run.calls) == 1
    command = run.calls[0]
    clips = [command[i + 1] for i, arg in enumerate(command) if arg == "-i"]
    assert clips == ["renders/sc1-sh1.mp4", "renders/sc2-sh2.mp4"]
    assert command[-1] == "film.mp4"


def test_assemble_film_skips_chain_with_missing_final_clip(capsys):
    project = _project(chains=[["sc1-sh1"], ["sc2-sh1", "sc2-sh2"]])
    results = [
        _result("sc1-sh1", uri="renders/sc1-sh1.mp4"),
        _result("sc2-sh1", uri="renders/sc2-sh1.mp4"),
        _result("sc2-sh2", status="failed", uri=None),
    ]
    run = FakeRun()

    out = assemble_film(project, results, "film.mp4", run=run)

    assert out == "film.mp4"
    command = run.calls[0]
    clips = [command[i + 1] for i, arg in enumerate(command) if arg == "-i"]
    assert clips == ["renders/sc1-sh1.mp4"]
    assert "skipping chain ending in 'sc2-sh2'" in capsys.readouterr().err


def test_assemble_film_returns_none_when_no_usable_clips():
    project = _project(chains=[["sc1-sh1"]])
    results = [_result("sc1-sh1", status="failed", uri=None)]
    run = FakeRun()

    out = assemble_film(project, results, "film.mp4", run=run)

    assert out is None
    assert not run.calls


def test_assemble_film_returns_none_when_no_chains():
    project = _project(chains=[])
    run = FakeRun()

    out = assemble_film(project, [], "film.mp4", run=run)

    assert out is None
    assert not run.calls
