"""Take library: previz clips rendered per shot, versioned by take number.

A *take* is one rendered attempt at a shot — typically a previz clip blocked
in Blender and rendered by Blender's own engine. A shot accumulates takes as
it gets re-blocked; the portal presents them side by side so one can be
picked to drive a generative render.

Directory layout::

    <root>/
        takes.json                       — index of every take (rebuildable)
        <scene_id>/<shot_id>/
            take_001.mp4                 — the clip
            take_001.json                — its Take record

The per-take JSON sidecars are the source of truth; ``takes.json`` is a
derived index. A take written while the index was stale — a crashed Blender,
a file copied in by hand — is recovered by `rebuild_manifest` rather than
lost, so the index can always be thrown away and regenerated.

`Take.video_path` is stored relative to the take root (absolute paths are
kept as-is), so a takes tree stays relocatable between the machine that
rendered it and the one serving it; `resolve_video` turns it back into a
real path. Same convention as `library.load_bible` and its stills.

schema.py is deliberately untouched: a take is a workflow artifact, not part
of the frozen project vocabulary.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

MANIFEST_NAME = "takes.json"
MANIFEST_VERSION = 1
TAKE_NUMBER_WIDTH = 3

_TAKE_STEM_RE = re.compile(r"^take_(\d+)$")

# How a take's camera was blocked.
BLOCKED_BY_MANUAL = "manual"  # hand-blocked in Blender
BLOCKED_BY_AUTO = "auto"      # deterministic mapping from the shot definition
BLOCKED_BY_LLM = "llm"        # an LLM interpreted the shot's prose camera move
BLOCKING_MODES: tuple[str, ...] = (BLOCKED_BY_MANUAL, BLOCKED_BY_AUTO, BLOCKED_BY_LLM)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class Take:
    """One rendered attempt at a shot.

    `media_id` is set once the clip has been uploaded to a render backend,
    and `renders` accumulates the ids of generative renders driven by this
    take — so the lineage from previz to final clip stays inspectable.
    """

    shot_id: str
    scene_id: str
    take_number: int
    video_path: str
    duration_s: float = 0.0
    camera_move: str = ""
    lens: str = ""
    framing: str = ""
    resolution: str = ""
    fps: int = 0
    blocked_by: str = BLOCKED_BY_MANUAL
    created_at: str = ""
    media_id: Optional[str] = None
    renders: list[str] = field(default_factory=list)
    notes: str = ""

    def __post_init__(self) -> None:
        if self.take_number < 1:
            raise ValueError(
                f"take for shot {self.shot_id}: take_number must be >= 1, "
                f"got {self.take_number}"
            )
        if self.blocked_by not in BLOCKING_MODES:
            raise ValueError(
                f"take {self.take_id}: blocked_by must be one of {BLOCKING_MODES}, "
                f"got {self.blocked_by!r}"
            )
        if not self.created_at:
            self.created_at = _now_iso()

    @property
    def take_id(self) -> str:
        """Stable cross-reference for one take, e.g. ``sc1-sh1#2``."""
        return f"{self.shot_id}#{self.take_number}"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Take":
        return cls(**data)


# --- Path convention --------------------------------------------------------


def take_stem(take_number: int) -> str:
    """``1`` -> ``take_001``. Zero-padded so takes sort lexically."""
    return f"take_{take_number:0{TAKE_NUMBER_WIDTH}d}"


def shot_dir(root: str | Path, scene_id: str, shot_id: str) -> Path:
    return Path(root) / scene_id / shot_id


def take_video_path(
    root: str | Path, scene_id: str, shot_id: str, take_number: int
) -> Path:
    return shot_dir(root, scene_id, shot_id) / f"{take_stem(take_number)}.mp4"


def take_record_path(
    root: str | Path, scene_id: str, shot_id: str, take_number: int
) -> Path:
    return shot_dir(root, scene_id, shot_id) / f"{take_stem(take_number)}.json"


def manifest_path(root: str | Path) -> Path:
    return Path(root) / MANIFEST_NAME


def resolve_video(take: Take, root: str | Path) -> Path:
    """Turn a take's stored `video_path` back into a real path.

    Relative paths resolve against `root`; absolute paths are kept as-is.
    """
    p = Path(take.video_path)
    return p if p.is_absolute() else Path(root) / p


def next_take_number(root: str | Path, scene_id: str, shot_id: str) -> int:
    """The next unused take number for a shot (1 when it has none yet).

    Scans every ``take_*`` file, not just the JSON records, so a take whose
    render died between writing the clip and writing its record still never
    has its number handed out twice.
    """
    directory = shot_dir(root, scene_id, shot_id)
    if not directory.is_dir():
        return 1
    highest = 0
    for path in directory.glob("take_*"):
        match = _TAKE_STEM_RE.match(path.stem)
        if match:
            highest = max(highest, int(match.group(1)))
    return highest + 1


# --- Read / write -----------------------------------------------------------


def save_take(take: Take, root: str | Path) -> Path:
    """Write a take's sidecar record and refresh the manifest.

    Returns the path of the written record. Creates the shot directory as
    needed, so Blender can render straight into `resolve_video(take, root)`.
    """
    directory = shot_dir(root, take.scene_id, take.shot_id)
    directory.mkdir(parents=True, exist_ok=True)

    record = take_record_path(root, take.scene_id, take.shot_id, take.take_number)
    record.write_text(json.dumps(take.to_dict(), indent=2), encoding="utf-8")

    rebuild_manifest(root)
    return record


def load_take(
    root: str | Path, scene_id: str, shot_id: str, take_number: int
) -> Take:
    record = take_record_path(root, scene_id, shot_id, take_number)
    return Take.from_dict(json.loads(record.read_text(encoding="utf-8")))


def scan_takes(root: str | Path) -> list[Take]:
    """Every take under `root`, read from the sidecar records themselves.

    Sorted by scene, then shot, then take number. A record that can't be
    parsed is skipped rather than raised on — one half-written file from a
    crashed render must not make the whole tree unreadable.
    """
    root_path = Path(root)
    if not root_path.is_dir():
        return []

    found: list[Take] = []
    for record in root_path.glob("*/*/take_*.json"):
        try:
            found.append(Take.from_dict(json.loads(record.read_text(encoding="utf-8"))))
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            continue
    found.sort(key=lambda take: (take.scene_id, take.shot_id, take.take_number))
    return found


def list_takes(
    root: str | Path,
    *,
    scene_id: Optional[str] = None,
    shot_id: Optional[str] = None,
) -> list[Take]:
    """Takes under `root`, optionally narrowed to one scene and/or shot."""
    takes = scan_takes(root)
    if scene_id is not None:
        takes = [take for take in takes if take.scene_id == scene_id]
    if shot_id is not None:
        takes = [take for take in takes if take.shot_id == shot_id]
    return takes


# --- Manifest ---------------------------------------------------------------


def rebuild_manifest(root: str | Path) -> Path:
    """Regenerate ``takes.json`` from the per-take records on disk.

    The manifest is a convenience index for the portal — grouped by shot so a
    takes gallery is one read — and is always safe to delete and rebuild.
    """
    root_path = Path(root)
    root_path.mkdir(parents=True, exist_ok=True)

    takes = scan_takes(root)
    by_shot: dict[str, list[dict[str, Any]]] = {}
    for take in takes:
        by_shot.setdefault(take.shot_id, []).append(take.to_dict())

    payload = {
        "version": MANIFEST_VERSION,
        "generated_at": _now_iso(),
        "take_count": len(takes),
        "shots": by_shot,
    }
    path = manifest_path(root)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def load_manifest(root: str | Path) -> dict[str, Any]:
    """Read ``takes.json``, or an empty manifest when it doesn't exist yet."""
    path = manifest_path(root)
    if not path.is_file():
        return {
            "version": MANIFEST_VERSION,
            "generated_at": "",
            "take_count": 0,
            "shots": {},
        }
    return json.loads(path.read_text(encoding="utf-8"))


# --- Construction from a Shot -----------------------------------------------


def new_take_for_shot(
    shot: Any,
    scene_id: str,
    root: str | Path,
    *,
    blocked_by: str = BLOCKED_BY_MANUAL,
    resolution: str = "",
    fps: int = 0,
) -> Take:
    """Build the next Take for `shot`, prefilled from its definition.

    `shot` is a schema.Shot (duck-typed so this module stays import-light):
    its camera_move / lens / framing / duration_s are copied onto the take,
    which is what lets Blender block a shot straight from the pipeline's own
    cinematography rather than re-deriving it.

    The take is returned unsaved — its video does not exist yet. Render into
    `resolve_video(take, root)`, then call `save_take`.
    """
    number = next_take_number(root, scene_id, shot.id)
    relative = Path(scene_id) / shot.id / f"{take_stem(number)}.mp4"
    return Take(
        shot_id=shot.id,
        scene_id=scene_id,
        take_number=number,
        video_path=str(relative),
        duration_s=float(shot.duration_s),
        camera_move=getattr(shot, "camera_move", ""),
        lens=getattr(shot, "lens", ""),
        framing=getattr(shot, "framing", ""),
        blocked_by=blocked_by,
        resolution=resolution,
        fps=fps,
    )
