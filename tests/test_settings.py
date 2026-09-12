"""Tests for the local settings screen.

Every test here mutates real process environment variables and a real file
on disk — that is the feature under test — so `isolated_environment` below
snapshots and restores the whole environment around each test rather than
tracking individual keys, and points MOVIECREW_SETTINGS_PATH at a fresh
file per test so nothing here ever touches a developer's real
~/.moviecrew/settings.json.
"""

from __future__ import annotations

import os
import stat
import sys

import pytest

from moviecrew import settings


@pytest.fixture(autouse=True)
def isolated_environment(tmp_path):
    snapshot = dict(os.environ)
    os.environ[settings.SETTINGS_PATH_ENV] = str(tmp_path / "settings.json")
    settings._applied_from_file.clear()
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(snapshot)
        settings._applied_from_file.clear()


# ---------------------------------------------------------------------- #
# The whitelist                                                           #
# ---------------------------------------------------------------------- #


def test_every_field_has_a_key_and_a_label():
    for field in settings.SETTINGS_FIELDS:
        assert field.key and field.label


def test_field_keys_are_unique():
    keys = [f.key for f in settings.SETTINGS_FIELDS]
    assert len(keys) == len(set(keys))


def test_the_asset_store_keys_are_present():
    """These are the ones that prompted the feature — pinned explicitly."""
    keys = {f.key for f in settings.SETTINGS_FIELDS}
    assert {
        "MOVIECREW_S3_ENDPOINT",
        "MOVIECREW_S3_BUCKET",
        "MOVIECREW_S3_ACCESS_KEY",
        "MOVIECREW_S3_SECRET_KEY",
        "MOVIECREW_S3_REGION",
        "MOVIECREW_ASSET_BASE_URL",
    } <= keys


def test_the_openrouter_key_is_secret():
    field = next(f for f in settings.SETTINGS_FIELDS if f.key == "OPENROUTER_API_KEY")
    assert field.secret is True


def test_the_bucket_name_is_not_secret():
    """Nothing sensitive about a bucket name; the UI shows it in full."""
    field = next(f for f in settings.SETTINGS_FIELDS if f.key == "MOVIECREW_S3_BUCKET")
    assert field.secret is False


# ---------------------------------------------------------------------- #
# File roundtrip and permissions                                          #
# ---------------------------------------------------------------------- #


def test_load_file_is_empty_before_anything_is_saved():
    assert settings.load_file() == {}


def test_save_and_load_roundtrip():
    settings.save_file({"OPENROUTER_API_KEY": "sk-abc123"})
    assert settings.load_file() == {"OPENROUTER_API_KEY": "sk-abc123"}


def test_save_merges_rather_than_replaces():
    settings.save_file({"OPENROUTER_API_KEY": "sk-abc123"})
    settings.save_file({"MOVIECREW_S3_BUCKET": "moviecrew"})
    assert settings.load_file() == {
        "OPENROUTER_API_KEY": "sk-abc123",
        "MOVIECREW_S3_BUCKET": "moviecrew",
    }


def test_an_empty_value_clears_a_saved_key():
    settings.save_file({"OPENROUTER_API_KEY": "sk-abc123"})
    settings.save_file({"OPENROUTER_API_KEY": ""})
    assert settings.load_file() == {}


def test_an_unknown_key_is_refused():
    with pytest.raises(settings.SettingsError, match="SOME_RANDOM_VAR"):
        settings.save_file({"SOME_RANDOM_VAR": "x"})


def test_refusing_an_unknown_key_saves_nothing_else_either():
    """All-or-nothing: a typo in one field must not silently save the rest."""
    with pytest.raises(settings.SettingsError):
        settings.save_file(
            {"OPENROUTER_API_KEY": "sk-abc123", "NOT_A_REAL_SETTING": "x"}
        )
    assert settings.load_file() == {}


def test_a_missing_file_is_read_as_empty_not_an_error():
    assert settings.settings_path().is_file() is False
    assert settings.load_file() == {}


def test_a_corrupt_file_is_read_as_empty_not_an_error():
    path = settings.settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{not valid json")
    assert settings.load_file() == {}


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX permission bits")
def test_the_file_is_written_owner_only():
    settings.save_file({"OPENROUTER_API_KEY": "sk-abc123"})
    mode = stat.S_IMODE(settings.settings_path().stat().st_mode)
    assert mode == stat.S_IRUSR | stat.S_IWUSR


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX permission bits")
def test_the_directory_is_written_owner_only():
    settings.save_file({"OPENROUTER_API_KEY": "sk-abc123"})
    mode = stat.S_IMODE(settings.settings_path().parent.stat().st_mode)
    assert mode == stat.S_IRWXU


def test_settings_path_is_overridable(tmp_path):
    custom = tmp_path / "elsewhere" / "config.json"
    os.environ[settings.SETTINGS_PATH_ENV] = str(custom)
    assert settings.settings_path() == custom


# ---------------------------------------------------------------------- #
# Precedence: a real env var beats a saved file, unless applying overrides #
# ---------------------------------------------------------------------- #


def test_apply_to_environ_fills_in_what_was_saved():
    settings.save_file({"OPENROUTER_API_KEY": "sk-abc123"})
    settings.apply_to_environ()
    assert os.environ["OPENROUTER_API_KEY"] == "sk-abc123"


def test_apply_to_environ_never_overrides_a_real_env_var():
    """A deployment that exported the key itself is never shadowed by a
    stray local file — this is the whole precedence rule."""
    os.environ["OPENROUTER_API_KEY"] = "from-the-shell"
    settings.save_file({"OPENROUTER_API_KEY": "from-the-file"})
    settings.apply_to_environ()
    assert os.environ["OPENROUTER_API_KEY"] == "from-the-shell"


def test_apply_to_environ_with_override_does_override():
    os.environ["OPENROUTER_API_KEY"] = "from-the-shell"
    settings.save_file({"OPENROUTER_API_KEY": "from-the-file"})
    settings.apply_to_environ(override=True)
    assert os.environ["OPENROUTER_API_KEY"] == "from-the-file"


# ---------------------------------------------------------------------- #
# apply_values: what the settings endpoint actually calls                 #
# ---------------------------------------------------------------------- #


def test_apply_values_takes_effect_immediately():
    settings.apply_values({"OPENROUTER_API_KEY": "sk-abc123"})
    assert os.environ["OPENROUTER_API_KEY"] == "sk-abc123"


def test_apply_values_persists_to_disk():
    settings.apply_values({"OPENROUTER_API_KEY": "sk-abc123"})
    assert settings.load_file() == {"OPENROUTER_API_KEY": "sk-abc123"}


def test_apply_values_overrides_an_existing_real_env_var():
    """Saving through the portal means 'use this now' — unlike startup's
    apply_to_environ(), this one always wins."""
    os.environ["OPENROUTER_API_KEY"] = "from-the-shell"
    settings.apply_values({"OPENROUTER_API_KEY": "from-the-ui"})
    assert os.environ["OPENROUTER_API_KEY"] == "from-the-ui"


def test_apply_values_rejects_an_unknown_key_and_changes_nothing():
    os.environ["OPENROUTER_API_KEY"] = "untouched"
    with pytest.raises(settings.SettingsError):
        settings.apply_values({"NOT_REAL": "x"})
    assert os.environ["OPENROUTER_API_KEY"] == "untouched"
    assert settings.load_file() == {}


def test_clearing_a_ui_saved_value_removes_it_from_the_environment():
    settings.apply_values({"OPENROUTER_API_KEY": "sk-abc123"})
    settings.apply_values({"OPENROUTER_API_KEY": ""})
    assert "OPENROUTER_API_KEY" not in os.environ


def test_clearing_a_field_never_touched_by_settings_leaves_a_real_env_var_alone():
    """The safety property this module exists to guarantee: emptying a
    settings-screen field for a key that was never set through it must not
    delete a real deployment's environment variable out from under it."""
    os.environ["OPENROUTER_API_KEY"] = "from-the-shell"
    settings.apply_values({"OPENROUTER_API_KEY": ""})
    assert os.environ["OPENROUTER_API_KEY"] == "from-the-shell"


def test_clearing_also_removes_it_from_the_saved_file():
    settings.apply_values({"OPENROUTER_API_KEY": "sk-abc123"})
    settings.apply_values({"OPENROUTER_API_KEY": ""})
    assert settings.load_file() == {}


# ---------------------------------------------------------------------- #
# describe_settings: what a browser is allowed to see                     #
# ---------------------------------------------------------------------- #


def test_an_unset_field_reports_unset():
    field = next(f for f in settings.describe_settings() if f["key"] == "OPENROUTER_API_KEY")
    assert field == {
        "key": "OPENROUTER_API_KEY",
        "label": "OpenRouter API key",
        "secret": True,
        "help": field["help"],
        "configured": False,
        "source": "unset",
        "value": "",
        "preview": "",
    }


def test_a_secret_never_reports_its_value():
    settings.apply_values({"OPENROUTER_API_KEY": "sk-super-secret-abc123"})
    field = next(f for f in settings.describe_settings() if f["key"] == "OPENROUTER_API_KEY")
    assert field["value"] == ""
    assert "sk-super-secret" not in str(field)


def test_a_secret_reports_only_its_last_four_characters():
    settings.apply_values({"OPENROUTER_API_KEY": "sk-super-secret-abc123"})
    field = next(f for f in settings.describe_settings() if f["key"] == "OPENROUTER_API_KEY")
    assert field["preview"] == "c123"
    assert field["configured"] is True


def test_a_non_secret_reports_its_actual_value():
    settings.apply_values({"MOVIECREW_S3_BUCKET": "moviecrew"})
    field = next(f for f in settings.describe_settings() if f["key"] == "MOVIECREW_S3_BUCKET")
    assert field["value"] == "moviecrew"
    assert field["preview"] == ""


def test_source_is_saved_after_apply_values():
    settings.apply_values({"OPENROUTER_API_KEY": "sk-abc123"})
    field = next(f for f in settings.describe_settings() if f["key"] == "OPENROUTER_API_KEY")
    assert field["source"] == "saved"


def test_source_is_environment_for_a_real_env_var_never_touched_by_settings():
    os.environ["OPENROUTER_API_KEY"] = "from-the-shell"
    field = next(f for f in settings.describe_settings() if f["key"] == "OPENROUTER_API_KEY")
    assert field["source"] == "environment"
    assert field["configured"] is True


def test_source_reflects_apply_to_environ_at_startup():
    settings.save_file({"OPENROUTER_API_KEY": "sk-abc123"})
    settings.apply_to_environ()
    field = next(f for f in settings.describe_settings() if f["key"] == "OPENROUTER_API_KEY")
    assert field["source"] == "saved"


def test_describe_settings_covers_every_field_exactly_once():
    described = [f["key"] for f in settings.describe_settings()]
    assert described == [f.key for f in settings.SETTINGS_FIELDS]
