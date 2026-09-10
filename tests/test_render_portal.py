"""Tests for the portal's generate-from-take endpoints.

Fully offline. With no OPENROUTER_API_KEY set the portal uses
FakeRenderClient, so the whole submit/poll/lineage path runs without a
network call or a cent spent — which is also the production default.
"""

from __future__ import annotations

import pytest

try:
    from fastapi.testclient import TestClient
except (ImportError, RuntimeError) as exc:
    pytest.skip(f"fastapi TestClient unavailable: {exc}", allow_module_level=True)

from moviecrew.portal.app import (  # noqa: E402
    _OPENROUTER_KEY_ENV,
    _PUBLIC_BASE_URL_ENV,
    _TAKES_ROOT_ENV,
    _render_clients,
    _render_jobs,
    app,
)
from moviecrew.takes import Take, load_take, save_take  # noqa: E402

client = TestClient(app)

_MP4 = b"\x00\x00\x00\x18ftypisom" + b"\x00" * 32
_PUBLIC = "https://previz.example.com"


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    """No key, so the fake backend is used and nothing can be billed."""
    monkeypatch.delenv(_OPENROUTER_KEY_ENV, raising=False)
    _render_jobs.clear()
    _render_clients.clear()


@pytest.fixture()
def takes_root(tmp_path, monkeypatch):
    root = tmp_path / "takes"
    root.mkdir()
    monkeypatch.setenv(_TAKES_ROOT_ENV, str(root))
    return root


@pytest.fixture()
def take(takes_root):
    record = Take(
        shot_id="sc1-sh1",
        scene_id="sc1",
        take_number=1,
        video_path="sc1/sc1-sh1/take_001.mp4",
        duration_s=8.0,
        camera_move="slow dolly-in",
    )
    save_take(record, takes_root)
    video = takes_root / "sc1" / "sc1-sh1" / "take_001.mp4"
    video.write_bytes(_MP4)
    return record


def _render(**overrides):
    body = {
        "scene_id": "sc1",
        "shot_id": "sc1-sh1",
        "take_number": 1,
        "prompt": "Mara hauls herself up the black-rock cliff path.",
    }
    body.update(overrides)
    return client.post("/api/render", json=body)


# ---------------------------------------------------------------------- #
# Models                                                                  #
# ---------------------------------------------------------------------- #


def test_models_report_the_fake_backend_when_no_key_is_set():
    body = client.get("/api/render/models").json()
    assert body["backend"] == "fake"
    assert body["live"] is False
    assert body["models"]


def test_models_expose_the_public_base_url(monkeypatch):
    monkeypatch.setenv(_PUBLIC_BASE_URL_ENV, _PUBLIC)
    assert client.get("/api/render/models").json()["public_base_url"] == _PUBLIC


# ---------------------------------------------------------------------- #
# Public URL requirement                                                  #
# ---------------------------------------------------------------------- #


def test_render_without_a_public_url_is_refused_with_a_usable_message(take, monkeypatch):
    """The provider fetches the take itself, so a loopback address is useless
    — better to say so up front than fail opaquely after submitting."""
    monkeypatch.delenv(_PUBLIC_BASE_URL_ENV, raising=False)
    res = _render()
    assert res.status_code == 400
    assert _PUBLIC_BASE_URL_ENV in res.json()["error"]


@pytest.mark.parametrize(
    "base", ["http://localhost:8000", "http://127.0.0.1:8000", "http://0.0.0.0:8000"]
)
def test_loopback_public_url_is_refused(take, monkeypatch, base):
    monkeypatch.setenv(_PUBLIC_BASE_URL_ENV, base)
    assert _render().status_code == 400


# ---------------------------------------------------------------------- #
# Submitting                                                              #
# ---------------------------------------------------------------------- #


def test_render_submits_and_returns_a_job(take, monkeypatch):
    monkeypatch.setenv(_PUBLIC_BASE_URL_ENV, _PUBLIC)
    body = _render().json()

    assert body["job_id"]
    assert body["shot_id"] == "sc1-sh1"
    assert body["status"] == "succeeded"
    assert body["take_id"] == "sc1-sh1#1"


def test_render_of_an_unknown_take_is_404(takes_root, monkeypatch):
    monkeypatch.setenv(_PUBLIC_BASE_URL_ENV, _PUBLIC)
    assert _render(take_number=99).status_code == 404


def test_estimate_only_reports_cost_without_submitting(take, monkeypatch):
    """Renders bill real money; the cost has to be visible before committing."""
    monkeypatch.setenv(_PUBLIC_BASE_URL_ENV, _PUBLIC)
    body = _render(estimate_only=True).json()

    assert body["estimate_only"] is True
    assert "cost" in body
    assert body["drives_motion_from_take"] is True
    assert _render_jobs == {}  # nothing was submitted


def test_estimate_reports_the_clamped_duration(take, monkeypatch):
    monkeypatch.setenv(_PUBLIC_BASE_URL_ENV, _PUBLIC)
    assert _render(estimate_only=True).json()["duration_s"] == 8


# ---------------------------------------------------------------------- #
# Polling and lineage                                                     #
# ---------------------------------------------------------------------- #


def test_poll_returns_the_job_state(take, monkeypatch):
    monkeypatch.setenv(_PUBLIC_BASE_URL_ENV, _PUBLIC)
    job_id = _render().json()["job_id"]

    body = client.get(f"/api/render/{job_id}").json()
    assert body["status"] == "succeeded"
    assert body["is_terminal"] is True


def test_finished_render_is_recorded_against_its_take(take, takes_root, monkeypatch):
    """Lineage from previz clip to final render must survive the process."""
    monkeypatch.setenv(_PUBLIC_BASE_URL_ENV, _PUBLIC)
    job_id = _render().json()["job_id"]
    client.get(f"/api/render/{job_id}")

    assert load_take(takes_root, "sc1", "sc1-sh1", 1).renders == [job_id]


def test_lineage_is_not_duplicated_on_repeated_polls(take, takes_root, monkeypatch):
    monkeypatch.setenv(_PUBLIC_BASE_URL_ENV, _PUBLIC)
    job_id = _render().json()["job_id"]
    client.get(f"/api/render/{job_id}")
    client.get(f"/api/render/{job_id}")

    assert load_take(takes_root, "sc1", "sc1-sh1", 1).renders == [job_id]


def test_polling_an_unknown_job_reports_failure_rather_than_crashing(takes_root):
    body = client.get("/api/render/does-not-exist").json()
    assert body["status"] == "failed"
    assert body["error"]
