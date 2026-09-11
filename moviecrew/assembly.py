"""Assembles a project's rendered chains into one film via ffmpeg.

What a chain produces depends on the backend that shot it. Veo extends a
clip from its own final frame, so a multi-shot chain comes back as one
cumulative take at the run's last shot. A backend that cannot continue a
take returns a clip per shot, and all of them belong in the cut. So
assemble_film follows the ExecutionRuns the backend actually performed
(MovieCrew.plan_execution), not the canonical editorial chains.

Command building is split into a pure function (build_concat_command) so
tests can assert on the ffmpeg invocation without shelling out; the real
subprocess call is parametrized as `run` for the same reason.
"""

from __future__ import annotations

import subprocess
import sys
from typing import Optional, Sequence

from .schema import Project
from .backend import ChainOutput, ExecutionRun, RenderResult

_RESOLUTION_HEIGHTS: dict[str, int] = {"720p": 720, "1080p": 1080, "4k": 2160}


def build_concat_command(
    clips: list[str],
    out_path: str,
    *,
    ffmpeg: str = "ffmpeg",
    target_resolution: str = "720p",
    fps: int = 24,
) -> list[str]:
    """The ffmpeg command to concatenate `clips` (in order) into `out_path`.

    Uses the concat *filter* (not the -c copy concat demuxer): each input is
    scaled to a common height/fps first, since chained vs. standalone clips
    can come back from a backend at different source dimensions and -c copy concat
    requires identical codecs/dimensions across inputs.

    Carries audio through (generated clips normally have a native audio track); this
    assumes every input clip has an audio stream — a missing-audio fallback
    (e.g. anullsrc) can come later if that stops holding.
    """
    height = _RESOLUTION_HEIGHTS[target_resolution]

    filter_parts = []
    concat_inputs = []
    for i in range(len(clips)):
        filter_parts.append(f"[{i}:v]scale=-2:{height},fps={fps}[v{i}]")
        concat_inputs.append(f"[v{i}][{i}:a]")
    filter_parts.append(f"{''.join(concat_inputs)}concat=n={len(clips)}:v=1:a=1[outv][outa]")

    cmd = [ffmpeg, "-y"]
    for clip in clips:
        cmd += ["-i", clip]
    cmd += ["-filter_complex", ";".join(filter_parts), "-map", "[outv]", "-map", "[outa]", out_path]
    return cmd


def assemble_film(
    project: Project,
    results: list[RenderResult],
    out_path: str,
    *,
    runs: Optional[Sequence[ExecutionRun]] = None,
    run=subprocess.run,
    ffmpeg: str = "ffmpeg",
    target_resolution: str = "720p",
    fps: int = 24,
) -> Optional[str]:
    """Concatenate the rendered footage, in screening order, into `out_path`.

    `runs` is how the backend actually executed the plan — pass what
    `MovieCrew.plan_execution()` returned for the same backend. It decides
    which clips carry the footage, and the canonical chains cannot: a chain
    of four shots is one cumulative clip on Veo and four separate clips on a
    backend that cannot continue a take, and assuming the first would drop
    three quarters of that chain on the floor.

    Omitting `runs` falls back to treating each canonical chain as one
    cumulative run, which is Veo's behaviour and was this function's only
    behaviour. That assumption is announced for any chain where it could be
    wrong, because being silently wrong here costs shots out of the film.

    Returns `out_path` on success, or None if there were no usable clips
    (e.g. every render failed). Skips and warns about any clip that is
    missing, failed, or has no uri.
    """
    render_plan = project.render_plan
    if render_plan is None or not render_plan.chains:
        print("assemble_film: project has no render plan / chains to assemble", file=sys.stderr)
        return None

    if runs is None:
        runs = [
            ExecutionRun(
                chain=tuple(chain),
                shot_ids=tuple(chain),
                output=ChainOutput.CUMULATIVE,
            )
            for chain in render_plan.chains
            if chain
        ]
        for multi_shot in (r for r in runs if len(r.shot_ids) > 1):
            print(
                f"assemble_film: no execution runs given; assuming the chain "
                f"ending in {multi_shot.shot_ids[-1]!r} came back as one "
                "cumulative clip. Pass runs=crew.plan_execution(project, "
                "backend) if the backend renders a clip per shot.",
                file=sys.stderr,
            )

    results_by_shot_id = {result.shot_id: result for result in results}

    clips: list[str] = []
    for execution_run in runs:
        for shot_id in execution_run.clip_shot_ids:
            result = results_by_shot_id.get(shot_id)
            if result is None or result.status != "succeeded" or not result.uri:
                print(
                    f"assemble_film: skipping {shot_id!r} "
                    "(no successful render to assemble)",
                    file=sys.stderr,
                )
                continue
            clips.append(result.uri)

    if not clips:
        print("assemble_film: no usable clips to assemble", file=sys.stderr)
        return None

    command = build_concat_command(
        clips, out_path, ffmpeg=ffmpeg, target_resolution=target_resolution, fps=fps
    )
    run(command, check=True)
    return out_path
