"""Visual Bible library: save and load a Bible as a reusable directory.

Directory layout::

    <dir>/
        bible.json      — serialised Bible (characters, locations, props, style…)
        stills/         — hand-supplied reference images; load_bible resolves
                          relative reference_images paths against this directory.

Paths in reference_images are never silently dropped, even when the file is
currently missing — anchor selection (moviecrew.rules.select_anchors) checks
existence at run time, so the library must faithfully round-trip what was saved.
"""

from __future__ import annotations

import json
from pathlib import Path

from .schema import Bible


def save_bible(bible: Bible, directory: str | Path) -> Path:
    """Serialise *bible* to ``<directory>/bible.json``.

    Creates ``<directory>/stills/`` (empty) as a convention so callers know
    where to place hand-made reference stills.  Returns the path of the
    written JSON file.
    """
    d = Path(directory)
    d.mkdir(parents=True, exist_ok=True)
    (d / "stills").mkdir(exist_ok=True)
    out = d / "bible.json"
    out.write_text(json.dumps(bible.to_dict(), indent=2), encoding="utf-8")
    return out


def load_bible(directory: str | Path) -> Bible:
    """Load a Bible from ``<directory>/bible.json``.

    Reference image paths that are relative (no directory component) are
    resolved against ``<directory>/stills/`` so hand-placed stills are found
    automatically.  Absolute paths are kept as-is.  Missing files are **not**
    dropped — the pipeline checks ``os.path.exists`` at run time.
    """
    d = Path(directory)
    data = json.loads((d / "bible.json").read_text(encoding="utf-8"))
    stills_dir = d / "stills"

    def _resolve(refs: list[str]) -> list[str]:
        result = []
        for ref in refs:
            p = Path(ref)
            if p.is_absolute():
                result.append(ref)
            else:
                result.append(str(stills_dir / p))
        return result

    # Rewrite reference_images in-place on each asset dict before handing to
    # Bible.from_dict so the nested constructors receive resolved paths.
    for c in data.get("characters", []):
        c["reference_images"] = _resolve(c.get("reference_images", []))
    for loc in data.get("locations", []):
        loc["reference_images"] = _resolve(loc.get("reference_images", []))
    for p in data.get("props", []):
        p["reference_images"] = _resolve(p.get("reference_images", []))

    return Bible.from_dict(data)
