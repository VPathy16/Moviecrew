"""Everything that touches the MovieCrew package, plus the bpy glue.

Kept apart from the operators and the UI so the boundary is obvious: the
interesting logic (parsing prose into camera geometry) lives in
`moviecrew.blocking` and is tested without Blender. What is here is the thin
part — putting the package on `sys.path`, reading the project file, and
pushing computed numbers onto real Blender datablocks.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any, Optional

# Populated by load_project(); read by the enum callbacks in __init__.
PROJECT: dict[str, Any] = {}
PROJECT_PATH: str = ""


def _moviecrew_imports() -> bool:
    try:
        importlib.import_module("moviecrew")
        return True
    except ImportError:
        return False


def ensure_moviecrew_importable(extra_path: str = "") -> Optional[str]:
    """Make `import moviecrew` work. Returns an error message, or None.

    Tries a plain import first, so a MovieCrew already installed into
    Blender's Python (pip install -e) needs no configuration at all. Falls
    back to the repository path from add-on preferences.
    """
    if _moviecrew_imports():
        return None

    if extra_path:
        root = Path(extra_path).expanduser()
        # Accept either the repo root or the package directory itself.
        if root.name == "moviecrew" and (root / "__init__.py").is_file():
            root = root.parent
        if (root / "moviecrew" / "__init__.py").is_file():
            sys.path.insert(0, str(root))
            # A failed import earlier in this session is cached; without this
            # the freshly added path would be ignored.
            importlib.invalidate_caches()
            if _moviecrew_imports():
                return None
            sys.path.remove(str(root))

    return (
        "MovieCrew package not found. Set the repository path in "
        "Preferences > Add-ons > MovieCrew, or pip install it into Blender."
    )


def load_project(path: str) -> Optional[str]:
    """Read a project.json written by the MovieCrew pipeline.

    Returns an error message, or None on success.
    """
    import json

    global PROJECT, PROJECT_PATH
    file = Path(path).expanduser()
    if not file.is_file():
        return f"No project file at {file}"
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return f"Could not read {file.name}: {exc}"

    if not data.get("scenes"):
        return f"{file.name} has no scenes — is it a MovieCrew project?"

    PROJECT = data
    PROJECT_PATH = str(file)
    return None


def scenes() -> list[dict[str, Any]]:
    return PROJECT.get("scenes", []) or []


def find_scene(scene_id: str) -> Optional[dict[str, Any]]:
    return next((s for s in scenes() if s.get("id") == scene_id), None)


def shots_in(scene_id: str) -> list[dict[str, Any]]:
    scene = find_scene(scene_id)
    return (scene or {}).get("shots", []) or []


def find_shot(scene_id: str, shot_id: str) -> Optional[dict[str, Any]]:
    return next((s for s in shots_in(scene_id) if s.get("id") == shot_id), None)


class _ShotView:
    """Adapts a shot dict to the attribute access `blocking.block_shot` wants.

    The project file is plain JSON, and re-importing schema.Shot just to
    re-validate data the pipeline already validated would be busywork.
    """

    __slots__ = ("id", "duration_s", "camera_move", "lens", "framing")

    def __init__(self, raw: dict[str, Any]) -> None:
        self.id = raw.get("id", "")
        self.duration_s = raw.get("duration_s", 0)
        self.camera_move = raw.get("camera_move", "")
        self.lens = raw.get("lens", "")
        self.framing = raw.get("framing", "")


def block_for(shot_raw: dict[str, Any], *, fps: int) -> Any:
    """Compute a CameraBlocking for a raw shot dict."""
    from moviecrew.blocking import block_shot

    return block_shot(_ShotView(shot_raw), fps=fps)


# --- bpy application --------------------------------------------------------


def apply_blocking(camera: Any, blocking: Any, scene: Any) -> None:
    """Key `blocking` onto a real Blender camera and set the frame range.

    Clears animation on both the object and its camera data — object-level
    `animation_data_clear()` does not touch the lens F-curve, which lives on
    the data, so a re-block would otherwise leave the old zoom behind.
    """
    scene.frame_start = blocking.frame_start
    scene.frame_end = blocking.frame_end
    scene.render.fps = blocking.fps

    camera.animation_data_clear()
    camera.data.animation_data_clear()

    for keyframe in blocking.keyframes:
        camera.location = keyframe.location
        camera.rotation_euler = keyframe.rotation_euler
        camera.data.lens = keyframe.focal_length_mm
        camera.keyframe_insert("location", frame=keyframe.frame)
        camera.keyframe_insert("rotation_euler", frame=keyframe.frame)
        camera.data.keyframe_insert("lens", frame=keyframe.frame)

    scene.frame_set(blocking.frame_start)


def configure_video_render(scene: Any, output_prefix: str, blocking: Any) -> None:
    """Point the scene at an H.264 MP4 covering the shot's frame range."""
    render = scene.render
    render.image_settings.file_format = "FFMPEG"
    render.ffmpeg.format = "MPEG4"
    render.ffmpeg.codec = "H264"
    render.ffmpeg.constant_rate_factor = "MEDIUM"
    render.ffmpeg.ffmpeg_preset = "GOOD"
    render.fps = blocking.fps
    render.filepath = output_prefix

    scene.frame_start = blocking.frame_start
    scene.frame_end = blocking.frame_end


def claim_rendered_file(directory: Path, stem: str, destination: Path) -> Optional[Path]:
    """Move Blender's actual output to `destination`.

    Blender decorates a movie filepath with the rendered frame range
    (``take_001.mp4`` becomes ``take_0010001-0000192.mp4``), and the exact
    decoration depends on format and settings. Rather than predict it, render
    with the take stem as a prefix and rename whatever came back — matching
    the name the take record already points at.
    """
    if destination.exists():
        return destination

    candidates = [
        path
        for path in directory.glob(f"{stem}*")
        if path.is_file() and path.suffix.lower() in {".mp4", ".mkv", ".mov", ".avi"}
    ]
    if not candidates:
        return None

    newest = max(candidates, key=lambda path: path.stat().st_mtime)
    if newest == destination:
        return destination
    newest.replace(destination)
    return destination
