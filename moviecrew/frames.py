"""Pull the first and last frame out of a rendered take.

A previz clip's value to a generative model is its composition: where the
camera starts and where it ends. No video model on OpenRouter accepts a
video as input — they take text, plus first/last-frame keyframes — so the
take contributes those two frames rather than its motion.

Command building is a pure function (`build_extract_command`) and the
subprocess call is parametrised as `run`, so the ffmpeg invocation is
testable without shelling out. Same split `assembly.py` uses.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Optional

FIRST_FRAME_SUFFIX = "-first.png"
LAST_FRAME_SUFFIX = "-last.png"


def build_extract_command(
    video: str,
    out_path: str,
    *,
    last: bool = False,
    ffmpeg: str = "ffmpeg",
) -> list[str]:
    """The ffmpeg command extracting one frame of `video` into `out_path`.

    The last frame is reached by seeking from the end of the file
    (`-sseof -0.1`) rather than by counting frames, so it needs no prior
    knowledge of the clip's duration or frame rate.
    """
    cmd = [ffmpeg, "-y"]
    if last:
        cmd += ["-sseof", "-0.1"]
    cmd += ["-i", video, "-frames:v", "1", "-update", "1", out_path]
    return cmd


def extract_frame(
    video: str,
    out_path: str,
    *,
    last: bool = False,
    run=subprocess.run,
    ffmpeg: str = "ffmpeg",
) -> Optional[str]:
    """Write one frame of `video` to `out_path`. Returns None on failure.

    Never raises: a missing ffmpeg, an unreadable clip, or a frame that
    simply didn't decode all return None, because a caller here is
    mid-workflow with a take in hand and wants a reportable failure rather
    than a traceback.
    """
    if not os.path.isfile(video):
        return None

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    cmd = build_extract_command(video, out_path, last=last, ffmpeg=ffmpeg)
    try:
        result = run(cmd, capture_output=True)
    except (OSError, ValueError):
        return None

    if getattr(result, "returncode", 1) != 0:
        return None
    return out_path if os.path.isfile(out_path) else None


def extract_bookend_frames(
    video: str,
    out_dir: str,
    *,
    stem: Optional[str] = None,
    run=subprocess.run,
    ffmpeg: str = "ffmpeg",
) -> tuple[Optional[str], Optional[str]]:
    """Extract a clip's opening and closing frame.

    Returns ``(first, last)``, either of which is None when that frame could
    not be produced. They are reported independently so a caller can still
    condition on the one that worked.
    """
    base = stem or Path(video).stem
    first = extract_frame(
        video,
        str(Path(out_dir) / f"{base}{FIRST_FRAME_SUFFIX}"),
        last=False,
        run=run,
        ffmpeg=ffmpeg,
    )
    last = extract_frame(
        video,
        str(Path(out_dir) / f"{base}{LAST_FRAME_SUFFIX}"),
        last=True,
        run=run,
        ffmpeg=ffmpeg,
    )
    return first, last
