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


# ---------------------------------------------------------------------- #
# Storing the render                                                      #
# ---------------------------------------------------------------------- #


def test_finished_render_is_downloaded_into_the_takes_tree(take, takes_root, monkeypatch):
    """A provider URL expires and the render cost money — the only copy must
    not be left on someone else's server."""
    monkeypatch.setenv(_PUBLIC_BASE_URL_ENV, _PUBLIC)
    job_id = _render().json()["job_id"]

    body = client.get(f"/api/render/{job_id}").json()
    saved = takes_root / "sc1" / "sc1-sh1" / "renders" / f"{job_id}.mp4"

    assert saved.is_file()
    assert body["local_path"] == str(saved)


def test_render_is_not_downloaded_twice(take, takes_root, monkeypatch):
    monkeypatch.setenv(_PUBLIC_BASE_URL_ENV, _PUBLIC)
    job_id = _render().json()["job_id"]

    client.get(f"/api/render/{job_id}")
    saved = takes_root / "sc1" / "sc1-sh1" / "renders" / f"{job_id}.mp4"
    saved.write_bytes(b"EDITED")
    client.get(f"/api/render/{job_id}")

    assert saved.read_bytes() == b"EDITED"


def test_a_download_failure_does_not_lose_the_provider_url(take, takes_root, monkeypatch):
    """Saving is best-effort; the result must stay visible either way."""
    from moviecrew.portal.app import _render_client

    monkeypatch.setenv(_PUBLIC_BASE_URL_ENV, _PUBLIC)
    job_id = _render().json()["job_id"]

    backend, _ = _render_client()
    monkeypatch.setattr(
        backend, "fetch", lambda *a, **k: (_ for _ in ()).throw(OSError("disk full"))
    )
    body = client.get(f"/api/render/{job_id}").json()

    assert body["local_path"] is None
    assert body["status"] == "succeeded"
    assert body["video_url"]


# ---------------------------------------------------------------------- #
# The real render path resolves canonical project state                   #
# ---------------------------------------------------------------------- #


def _add_take(root, *, scene_id="sc1", shot_id="sc1-sh1", number=1):
    record = Take(
        shot_id=shot_id,
        scene_id=scene_id,
        take_number=number,
        video_path=f"{scene_id}/{shot_id}/take_{number:03d}.mp4",
        duration_s=8.0,
    )
    save_take(record, root)
    video = root / scene_id / shot_id / f"take_{number:03d}.mp4"
    video.parent.mkdir(parents=True, exist_ok=True)
    video.write_bytes(_MP4)
    return record


def _fake_client():
    """The FakeRenderClient the portal is currently using."""
    from moviecrew.portal.app import _render_client

    backend, err = _render_client()
    assert err is None
    return backend


def _plan_session(client):
    res = client.post("/api/plan", json={"concept": "A keeper and a sea spirit."})
    assert res.status_code == 200
    return res.json()["session_id"]


def test_render_resolves_the_shot_intent_from_the_session(takes_root, monkeypatch):
    """The browser sends a session id, not a reconstructed prompt: the server
    reads the shot's intent out of the project it already holds."""
    from moviecrew.portal.app import _sessions

    monkeypatch.setenv("MOVIECREW_PUBLIC_BASE_URL", "https://previz.example.test")
    session_id = _plan_session(client)
    project = _sessions[session_id].project
    shot = project.scenes[0].shots[0]
    intent = next(i for i in project.render_plan.intents if i.shot_id == shot.id)
    _add_take(takes_root, scene_id=shot.scene_id, shot_id=shot.id)

    res = client.post(
        "/api/render",
        json={
            "scene_id": shot.scene_id,
            "shot_id": shot.id,
            "take_number": 1,
            "session_id": session_id,
        },
    )
    assert res.status_code == 200, res.json()

    spec, _model = _fake_client().submitted[-1]
    assert spec.prompt == intent.description
    assert spec.shot_id == shot.id


def test_storyboard_approval_changes_the_next_render_request(takes_root, monkeypatch):
    """The end-to-end regression: approve a board, then render, and the
    request carries the approved still."""
    from moviecrew.image import MockImageProvider
    from moviecrew.portal.app import _sessions

    class Promoting(MockImageProvider):
        promotes_references = True

    monkeypatch.setenv("MOVIECREW_PUBLIC_BASE_URL", "https://previz.example.test")
    session_id = _plan_session(client)
    session = _sessions[session_id]
    session.image_provider = Promoting()

    shot = session.project.scenes[0].shots[0]
    shot.consistency_anchor = True
    _add_take(takes_root, scene_id=shot.scene_id, shot_id=shot.id)

    body = {
        "scene_id": shot.scene_id,
        "shot_id": shot.id,
        "take_number": 1,
        "session_id": session_id,
    }
    assert client.post("/api/render", json=body).status_code == 200
    before = list(_fake_client().submitted[-1][0].reference_images)

    client.post("/api/storyboard", json={"session_id": session_id})
    client.post("/api/storyboard/approve", json={"session_id": session_id})

    assert client.post("/api/render", json=body).status_code == 200
    after = list(_fake_client().submitted[-1][0].reference_images)

    assert after != before, "approval must reach the request"
    assert after[0].endswith(".png")
    assert after[0] in shot.reference_image_ids


def test_render_without_a_session_or_prompt_is_refused(takes_root):
    _add_take(takes_root)
    res = client.post(
        "/api/render",
        json={"scene_id": "sc1", "shot_id": "sc1-sh1", "take_number": 1},
    )
    assert res.status_code == 400
    assert "session_id" in res.json()["error"]


def test_a_session_that_lacks_the_shot_is_an_error_not_a_silent_fallback(takes_root):
    _add_take(takes_root, scene_id="sc9", shot_id="sc9-sh1")
    session_id = _plan_session(client)
    res = client.post(
        "/api/render",
        json={
            "scene_id": "sc9",
            "shot_id": "sc9-sh1",
            "take_number": 1,
            "session_id": session_id,
        },
    )
    assert res.status_code == 404
    assert "disagree" in res.json()["error"]


# ---------------------------------------------------------------------- #
# Asset store: where a driving take is fetched from                       #
# ---------------------------------------------------------------------- #


@pytest.fixture()
def no_bucket(monkeypatch):
    from moviecrew.portal.app import _asset_stores

    for var in ("MOVIECREW_S3_BUCKET", "MOVIECREW_S3_ENDPOINT",
                "MOVIECREW_S3_ACCESS_KEY", "MOVIECREW_S3_SECRET_KEY",
                "MOVIECREW_ASSET_BASE_URL"):
        monkeypatch.delenv(var, raising=False)
    _asset_stores.clear()
    yield
    _asset_stores.clear()


def test_health_reports_the_asset_store(takes_root, no_bucket):
    body = client.get("/api/health").json()
    assert body["asset_store"] == "local"
    assert body["asset_store_public"] is False


def test_health_reports_a_public_bucket(takes_root, monkeypatch):
    from moviecrew.portal.app import _asset_stores

    _asset_stores.clear()
    monkeypatch.setenv("MOVIECREW_S3_BUCKET", "moviecrew")
    monkeypatch.setenv("MOVIECREW_S3_ENDPOINT", "https://acct.r2.cloudflarestorage.com")
    monkeypatch.setenv("MOVIECREW_S3_ACCESS_KEY", "AK")
    monkeypatch.setenv("MOVIECREW_S3_SECRET_KEY", "SK")
    monkeypatch.setenv("MOVIECREW_ASSET_BASE_URL", "https://pub-abc.r2.dev")

    body = client.get("/api/health").json()
    assert body["asset_store"] == "s3"
    assert body["asset_store_public"] is True
    _asset_stores.clear()


def test_a_take_is_uploaded_and_its_cdn_url_drives_the_render(takes_root, take, monkeypatch):
    """With a bucket configured the take is PUT once under a stable key and
    the render is pointed at the CDN, not at this process."""
    from moviecrew.assets import S3AssetStore
    from moviecrew.portal.app import _asset_stores

    calls = []

    def transport(method, url, headers, body):
        calls.append({"method": method, "url": url, "headers": headers})
        return b""

    store = S3AssetStore(
        bucket="moviecrew",
        endpoint="https://acct.r2.cloudflarestorage.com",
        access_key="AK",
        secret_key="SK",
        public_base="https://pub-abc.r2.dev",
        transport=transport,
    )
    _asset_stores.clear()
    monkeypatch.setattr("moviecrew.portal.app._asset_store", lambda: store)

    res = _render(prompt="Mara hauls herself up the cliff.")
    assert res.status_code == 200, res.json()

    assert calls and calls[0]["method"] == "PUT"
    assert calls[0]["url"].endswith("/moviecrew/takes/sc1/sc1-sh1/take_001.mp4")
    assert calls[0]["headers"]["content-type"] == "video/mp4"

    spec, _model = _fake_client().submitted[-1]
    assert spec.reference_video == "https://pub-abc.r2.dev/takes/sc1/sc1-sh1/take_001.mp4"
    _asset_stores.clear()


def test_without_a_bucket_the_portal_address_is_used(takes_root, take, monkeypatch, no_bucket):
    monkeypatch.setenv(_PUBLIC_BASE_URL_ENV, "https://previz.example.test")
    res = _render(prompt="x")
    assert res.status_code == 200

    spec, _model = _fake_client().submitted[-1]
    assert spec.reference_video.startswith("https://previz.example.test/api/takes/")


def test_with_nowhere_to_serve_from_the_error_names_the_knobs(takes_root, take, monkeypatch, no_bucket):
    monkeypatch.delenv(_PUBLIC_BASE_URL_ENV, raising=False)
    res = _render(prompt="x")
    assert res.status_code == 400
    message = res.json()["error"]
    assert "MOVIECREW_S3_BUCKET" in message
    assert _PUBLIC_BASE_URL_ENV in message
