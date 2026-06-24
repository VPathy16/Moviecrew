"""Assembles a project's rendered chains into one film via ffmpeg.

Each render_plan chain produces one continuous clip: for a multi-shot
chain that's the cumulative take at chain[-1] (Veo extension output is
cumulative — predecessor + ~7s); for a singleton chain it's that shot's
own clip. assemble_film concatenates those clips, in chain order, into a
single output file.

Command building is split into a pure function (build_concat_command) so
tests can assert on the ffmpeg invocation without shelling out; the real
subprocess call is parametrized as `run` for the same reason.
"""

from __future__ import annotations

import subprocess
import sys
from typing import Optional

from .schema import Project
from .video import RenderResult

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
    can come back from Veo at different source dimensions and -c copy concat
    requires identical codecs/dimensions across inputs.

    Carries audio through (Veo clips always have a native audio track); this
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
    run=subprocess.run,
    ffmpeg: str = "ffmpeg",
    target_resolution: str = "720p",
    fps: int = 24,
) -> Optional[str]:
    """Concatenate each chain's final clip, in chain order, into `out_path`.

    Returns `out_path` on success, or None if there were no usable clips to
    assemble (e.g. every chain's final render failed). Skips and warns about
    any chain whose final result is missing, failed, or has no uri.
    """
    render_plan = project.render_plan
    if render_plan is None or not render_plan.chains:
        print("assemble_film: project has no render plan / chains to assemble", file=sys.stderr)
        return None

    results_by_shot_id = {result.shot_id: result for result in results}

    clips: list[str] = []
    for chain in render_plan.chains:
        final_shot_id = chain[-1]
        result = results_by_shot_id.get(final_shot_id)
        if result is None or result.status != "succeeded" or not result.uri:
            print(
                f"assemble_film: skipping chain ending in {final_shot_id!r} "
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
