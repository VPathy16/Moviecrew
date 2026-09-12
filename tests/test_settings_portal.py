"""Tests for the settings endpoints and their effect on the rest of the
portal.

Fully offline. The point of these tests is the wiring: that a value saved
through /api/settings is what /api/health, /api/render/models and the
render/asset-store caches actually see on the very next request, with no
restart — and that a secret never reappears in a response.
"""

from __future__ import annotations

import os

import pytest

try:
    from fastapi.testclient import TestClient
except (ImportError, RuntimeError) as exc:
    pytest.skip(f"fastapi TestClient unavailable: {exc}", allow_module_level=True)

from moviecrew import settings  # noqa: E402
from moviecrew.portal.app import (  # noqa: E402
    _OPENROUTER_KEY_ENV,
    _asset_stores,
    _render_clients,
    app,
)

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_environment(tmp_path):
    """Same rationale as tests/test_settings.py: this endpoint mutates real
    process env vars, so snapshot and restore the whole environment, and
    keep the settings file (and every env-keyed cache) confined to this
    test."""
    snapshot = dict(os.environ)
    os.environ[settings.SETTINGS_PATH_ENV] = str(tmp_path / "settings.json")
    os.environ.pop(_OPENROUTER_KEY_ENV, None)
    settings._applied_from_file.clear()
    _render_clients.clear()
    _asset_stores.clear()
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(snapshot)
        settings._applied_from_file.clear()
        _render_clients.clear()
        _asset_stores.clear()


# ---------------------------------------------------------------------- #
# GET /api/settings                                                        #
# ---------------------------------------------------------------------- #


def test_get_settings_lists_every_field():
    res = client.get("/api/settings")
    assert res.status_code == 200
    keys = [f["key"] for f in res.json()["fields"]]
    assert keys == [f.key for f in settings.SETTINGS_FIELDS]


def test_get_settings_never_carries_a_configured_secret():
    client.post("/api/settings", json={"values": {"OPENROUTER_API_KEY": "sk-abc123"}})
    res = client.get("/api/settings")
    assert "sk-abc123" not in res.text


def test_get_settings_reports_the_settings_path():
    res = client.get("/api/settings")
    assert res.json()["settings_path"] == str(settings.settings_path())


# ---------------------------------------------------------------------- #
# POST /api/settings                                                       #
# ---------------------------------------------------------------------- #


def test_post_settings_takes_effect_before_the_response_is_even_read():
    client.post("/api/settings", json={"values": {"OPENROUTER_API_KEY": "sk-abc123"}})
    assert os.environ["OPENROUTER_API_KEY"] == "sk-abc123"


def test_post_settings_response_never_carries_the_secret_back():
    res = client.post(
        "/api/settings", json={"values": {"OPENROUTER_API_KEY": "sk-abc123"}}
    )
    assert res.status_code == 200
    assert "sk-abc123" not in res.text


def test_post_settings_rejects_an_unknown_key():
    res = client.post("/api/settings", json={"values": {"NOT_A_SETTING": "x"}})
    assert res.status_code == 400
    assert "NOT_A_SETTING" in res.json()["error"]


def test_an_unknown_key_saves_nothing():
    client.post("/api/settings", json={"values": {"NOT_A_SETTING": "x"}})
    assert settings.load_file() == {}


def test_settings_survive_a_simulated_restart():
    """apply_to_environ() is what the portal calls at import; simulate one
    here rather than actually reimporting the module."""
    client.post("/api/settings", json={"values": {"OPENROUTER_API_KEY": "sk-abc123"}})
    del os.environ["OPENROUTER_API_KEY"]
    settings.apply_to_environ()
    assert os.environ["OPENROUTER_API_KEY"] == "sk-abc123"


# ---------------------------------------------------------------------- #
# The point of the feature: other endpoints see the change immediately    #
# ---------------------------------------------------------------------- #


def test_saving_the_key_flips_the_default_backend_reported_by_health():
    assert client.get("/api/health").json()["default_backend"] == "mock"
    client.post("/api/settings", json={"values": {"OPENROUTER_API_KEY": "sk-abc123"}})
    assert client.get("/api/health").json()["default_backend"] == "openrouter"


def test_clearing_the_key_flips_it_back_to_mock():
    client.post("/api/settings", json={"values": {"OPENROUTER_API_KEY": "sk-abc123"}})
    assert client.get("/api/health").json()["default_backend"] == "openrouter"
    client.post("/api/settings", json={"values": {"OPENROUTER_API_KEY": ""}})
    assert client.get("/api/health").json()["default_backend"] == "mock"


def test_saving_the_takes_root_changes_what_health_reports(tmp_path):
    custom = tmp_path / "custom-takes"
    res = client.post(
        "/api/settings", json={"values": {"MOVIECREW_TAKES_ROOT": str(custom)}}
    )
    assert res.status_code == 200
    assert client.get("/api/health").json()["takes_root"] == str(custom)


def test_saving_the_bucket_name_changes_the_asset_store_reported_by_health():
    assert client.get("/api/health").json()["asset_store"] == "local"
    client.post(
        "/api/settings",
        json={
            "values": {
                "MOVIECREW_S3_BUCKET": "moviecrew",
                "MOVIECREW_S3_ENDPOINT": "https://example.r2.cloudflarestorage.com",
                "MOVIECREW_S3_ACCESS_KEY": "AKIA...",
                "MOVIECREW_S3_SECRET_KEY": "shh",
            }
        },
    )
    assert client.get("/api/health").json()["asset_store"] == "s3"


def test_saving_a_public_asset_base_url_reports_the_store_as_public():
    client.post(
        "/api/settings",
        json={
            "values": {
                "MOVIECREW_S3_BUCKET": "moviecrew",
                "MOVIECREW_S3_ENDPOINT": "https://example.r2.cloudflarestorage.com",
                "MOVIECREW_S3_ACCESS_KEY": "AKIA...",
                "MOVIECREW_S3_SECRET_KEY": "shh",
                "MOVIECREW_ASSET_BASE_URL": "https://pub-abcdef.r2.dev",
            }
        },
    )
    assert client.get("/api/health").json()["asset_store_public"] is True
