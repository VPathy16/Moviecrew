"""A local settings screen for keys the portal otherwise reads from the
process environment.

Every credential and config value the portal uses — the OpenRouter key,
the R2/S3 credentials, the public base URLs — is read with
`os.environ.get(...)`, by design (see `portal/app.py`'s module docstring):
a browser cannot make this process talk to a bucket or a backend it wasn't
told about. That is still true here. This module does not add a second
way to configure the portal per request; it adds a *local* place to store
the same environment variables between restarts, so a solo user is not
stuck re-exporting five values by hand every time the process starts.

Settings live in one JSON file on the machine running the portal —
`~/.moviecrew/settings.json` by default, `$MOVIECREW_SETTINGS_PATH` to
move it — written with owner-only permissions. Only a fixed whitelist of
keys can be stored (`SETTINGS_FIELDS`); nothing else is accepted, so this
is not a general environment-variable injection surface.

Precedence is deliberate. `apply_to_environ()` (called once, by the portal,
at startup) fills in a whitelisted variable only if the real process
environment does not already have it — a value a deployment actually
exported always wins over a stray local file. `apply_values()` (called by
the settings endpoint on every save) is the one exception: saving through
the portal means "use this now", so it always overrides the running
process's environment and takes effect on the very next request, no
restart needed.

Clearing a field only ever removes what this module itself put there.
Emptying a field that was never saved through settings — its value came
from a real environment variable the process inherited — leaves that
environment variable alone; the settings file simply stops overriding it,
which is nothing, since it never did.

Secret fields are never sent back to a browser in full. `describe_settings()`
reports whether each field is set and, for a secret, only its last four
characters — enough to confirm which key is loaded without ever putting the
whole thing back on the wire.
"""

from __future__ import annotations

import json
import os
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

SETTINGS_PATH_ENV = "MOVIECREW_SETTINGS_PATH"
_DEFAULT_SETTINGS_PATH = Path.home() / ".moviecrew" / "settings.json"


@dataclass(frozen=True)
class SettingsField:
    key: str  # the environment variable name this field sets
    label: str  # shown in the settings screen
    secret: bool  # mask the value everywhere it could reach a browser
    help: str = ""


# Exactly the environment variables the rest of the portal already reads.
# Adding one here is the only way to make it settable through the UI —
# `save_file` refuses anything not in this list.
SETTINGS_FIELDS: tuple[SettingsField, ...] = (
    SettingsField(
        "OPENROUTER_API_KEY",
        "OpenRouter API key",
        secret=True,
        help="Powers the crew's agents, storyboard stills, and generative renders.",
    ),
    SettingsField(
        "ANTHROPIC_API_KEY",
        "Anthropic API key",
        secret=True,
        help="Only needed for the direct-to-Anthropic backend.",
    ),
    SettingsField(
        "MOVIECREW_PUBLIC_BASE_URL",
        "Portal public URL",
        secret=False,
        help=(
            "Where this portal is reachable from the internet (a tunnel or a "
            "LAN address), so a render backend can fetch the driving take. "
            "Never a loopback address."
        ),
    ),
    SettingsField(
        "MOVIECREW_TAKES_ROOT",
        "Takes directory",
        secret=False,
        help="Where Blender writes previz takes. Default: ./takes",
    ),
    SettingsField(
        "MOVIECREW_S3_ENDPOINT",
        "R2 / S3 endpoint",
        secret=False,
        help="e.g. https://<account id>.r2.cloudflarestorage.com",
    ),
    SettingsField("MOVIECREW_S3_BUCKET", "R2 / S3 bucket", secret=False),
    SettingsField("MOVIECREW_S3_ACCESS_KEY", "R2 / S3 access key", secret=True),
    SettingsField("MOVIECREW_S3_SECRET_KEY", "R2 / S3 secret key", secret=True),
    SettingsField(
        "MOVIECREW_S3_REGION", "R2 / S3 region", secret=False, help="'auto' for R2."
    ),
    SettingsField(
        "MOVIECREW_ASSET_BASE_URL",
        "Asset public base URL",
        secret=False,
        help="e.g. https://pub-xxxx.r2.dev, or a custom domain once attached.",
    ),
)

_FIELDS_BY_KEY: dict[str, SettingsField] = {field.key: field for field in SETTINGS_FIELDS}

# Which currently-set environment variables this module itself put there —
# via apply_to_environ() or apply_values() — as opposed to ones the process
# already had. Clearing a field only ever pops a key recorded here; see the
# module docstring. Process-lifetime state, deliberately: it answers "did
# settings.py set this?", which nothing else can reconstruct after the fact.
_applied_from_file: set[str] = set()


class SettingsError(ValueError):
    """A settings payload named a key this portal does not recognise."""


def settings_path() -> Path:
    configured = os.environ.get(SETTINGS_PATH_ENV)
    return Path(configured).expanduser() if configured else _DEFAULT_SETTINGS_PATH


def load_file(path: Optional[Path] = None) -> dict[str, str]:
    """Whatever is saved on disk, or {} if there is nothing yet.

    Never raises: a missing, unreadable, or corrupt file is indistinguishable
    from "nothing saved" as far as callers are concerned, and the portal
    should still start.
    """
    path = path or settings_path()
    try:
        raw = path.read_text()
    except OSError:
        return {}
    try:
        data = json.loads(raw)
    except ValueError:
        return {}
    if not isinstance(data, dict):
        return {}
    return {k: v for k, v in data.items() if isinstance(k, str) and isinstance(v, str)}


def save_file(values: dict[str, str], *, path: Optional[Path] = None) -> None:
    """Merge `values` into the settings file, keyed by environment variable.

    Refuses any key outside `SETTINGS_FIELDS`. An empty string clears a key
    rather than storing it, so clearing a field in the UI actually removes
    it from the file instead of persisting an empty override.

    Written owner-only (0700 directory, 0600 file) since this file can hold
    plaintext credentials.
    """
    unknown = sorted(set(values) - set(_FIELDS_BY_KEY))
    if unknown:
        raise SettingsError(f"unknown setting(s): {', '.join(unknown)}")

    path = path or settings_path()
    current = load_file(path)
    for key, value in values.items():
        if value:
            current[key] = value
        else:
            current.pop(key, None)

    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(path.parent, stat.S_IRWXU)  # 0700: owner only
    except OSError:
        pass
    path.write_text(json.dumps(current, indent=2, sort_keys=True))
    try:
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)  # 0600: owner read/write only
    except OSError:
        pass


def apply_to_environ(*, override: bool = False) -> None:
    """Load the settings file and set process env vars from it.

    Without `override` (the portal's startup call), a variable already
    present in the real process environment is left alone — a deployment
    that exported OPENROUTER_API_KEY itself is never silently shadowed by a
    leftover local file. `override=True` is for `apply_values`: saving
    through the portal means "use this now".
    """
    for key, value in load_file().items():
        if override or key not in os.environ:
            os.environ[key] = value
            _applied_from_file.add(key)


def apply_values(values: dict[str, str]) -> None:
    """Save `values` and apply them to this process's environment at once.

    The one call the settings endpoint needs: after this returns, the very
    next request sees the new configuration, with no restart. Raises
    `SettingsError` (and changes nothing) if `values` names an unknown key.
    """
    save_file(values)  # validates first; nothing below runs on a bad key
    for key, value in values.items():
        if value:
            os.environ[key] = value
            _applied_from_file.add(key)
        elif key in _applied_from_file:
            # Only remove what this module itself added. A real environment
            # variable the process inherited from its shell is left alone —
            # clearing a saved override just means it no longer overrides.
            os.environ.pop(key, None)
            _applied_from_file.discard(key)


def describe_settings() -> list[dict]:
    """Every known field's current state, safe to hand to a browser.

    A secret field never reports its value — only whether one is set and,
    if so, its last four characters, enough to recognise which key is
    loaded without it ever crossing the wire again. A non-secret field (a
    bucket name, a region, a public URL) reports its actual value, since
    none of those are sensitive and seeing them is the point of a settings
    screen.
    """
    out = []
    for field in SETTINGS_FIELDS:
        current = os.environ.get(field.key, "")
        configured = bool(current)
        out.append(
            {
                "key": field.key,
                "label": field.label,
                "secret": field.secret,
                "help": field.help,
                "configured": configured,
                "source": (
                    "saved" if field.key in _applied_from_file
                    else "environment" if configured
                    else "unset"
                ),
                "value": "" if field.secret else current,
                "preview": f"{current[-4:]}" if field.secret and configured else "",
            }
        )
    return out
