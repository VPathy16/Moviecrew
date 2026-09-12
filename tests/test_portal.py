"""Tests for the optional FastAPI portal (the PLAN path only).

Fully offline: uses fastapi.testclient.TestClient and the mock LLM backend,
no network and no real API key needed. Skips cleanly when the test client
isn't available (the `portal` extra is optional).

Guarded on TestClient itself rather than on `fastapi`, and catching
RuntimeError as well as ImportError: fastapi can import perfectly while
`fastapi.testclient` still fails, because starlette raises RuntimeError —
not ImportError — when its HTTP client dependency is missing. A plain
`importorskip("fastapi")` lets that through as a hard collection error.
"""

import json
from pathlib import Path

import pytest

try:
    from fastapi.testclient import TestClient
except (ImportError, RuntimeError) as exc:
    pytest.skip(f"fastapi TestClient unavailable: {exc}", allow_module_level=True)

import moviecrew.mock as mock_module  # noqa: E402
from moviecrew.portal.app import app  # noqa: E402

client = TestClient(app)


@pytest.fixture
def failing_continuity(monkeypatch):
    """Simulate the reported failure: continuity fails after everything
    else generated successfully. Patches the mock backend's own class
    method so /api/plan's real code path (crew.make() through the mock
    LLM) is exercised, not a stand-in for it.
    """
    original = mock_module.MockLLMClient.complete_json

    def sometimes_failing(self, *, task, system, user):
        if task == "continuity":
            raise RuntimeError("simulated continuity outage")
        return original(self, task=task, system=system, user=user)

    monkeypatch.setattr(mock_module.MockLLMClient, "complete_json", sometimes_failing)


def test_health_lists_backends_and_detail_levels():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert "mock" in data["backends"]
    assert "anthropic" in data["backends"]
    assert set(data["detail_levels"]) == {"lean", "cinematic", "maximal"}


def test_index_serves_html():
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]


def test_plan_with_mock_backend_returns_full_project():
    res = client.post("/api/plan", json={"concept": "A lighthouse keeper meets a sea spirit."})
    assert res.status_code == 200
    project = res.json()

    assert project["title"]
    assert project["scenes"]
    for scene in project["scenes"]:
        assert scene["shots"]

    render_plan = project["render_plan"]
    assert render_plan["intents"]
    assert render_plan["chains"]
    assert render_plan["order"]

    for intent in render_plan["intents"]:
        assert intent["description"]
        assert "negative" in intent
        assert intent["aspect_ratio"] == "16:9"


def test_plan_with_explicit_detail_level():
    res = client.post(
        "/api/plan", json={"concept": "A heist at a museum.", "backend": "mock", "detail": "lean"}
    )
    assert res.status_code == 200
    assert res.json()["render_plan"]["intents"]


def test_plan_rejects_unknown_backend():
    res = client.post("/api/plan", json={"concept": "x", "backend": "not-a-backend"})
    assert res.status_code == 400
    body = res.json()
    assert "error" in body
    assert "traceback" not in body["error"].lower()


def test_plan_rejects_unknown_detail():
    res = client.post("/api/plan", json={"concept": "x", "detail": "not-a-level"})
    assert res.status_code == 400
    assert "error" in res.json()


# ---------------------------------------------------------------------- #
# Continuity failing must not cost the plan already generated             #
# ---------------------------------------------------------------------- #


def test_plan_returns_the_project_even_when_continuity_fails(failing_continuity):
    """The reported failure, through the actual endpoint: a large project
    generated every scene/shot/prompt, then continuity hit finish_reason=
    "length" and /api/plan failed, taking the whole generated project with
    it. It no longer does."""
    res = client.post("/api/plan", json={"concept": "A lighthouse keeper meets a sea spirit."})
    assert res.status_code == 200

    project = res.json()
    assert project["title"]
    assert project["scenes"]
    for scene in project["scenes"]:
        assert scene["shots"]
    assert project["render_plan"]["intents"]
    assert project["session_id"]


def test_the_continuity_failure_is_visible_as_a_project_level_flag(failing_continuity):
    res = client.post("/api/plan", json={"concept": "A lighthouse keeper meets a sea spirit."})
    flags = res.json()["render_plan"]["flags"]
    warnings = [f for f in flags if f["target"] == "project"]
    assert len(warnings) == 1
    assert warnings[0]["kind"] == "warning"
    assert "simulated continuity outage" in warnings[0]["message"]


# ---------------------------------------------------------------------- #
# Save Project: works whether or not continuity completed                 #
# ---------------------------------------------------------------------- #


def test_save_project_succeeds_after_a_normal_plan():
    plan_res = client.post("/api/plan", json={"concept": "A quiet heist."})
    session_id = plan_res.json()["session_id"]

    save_res = client.post(f"/api/session/{session_id}/save")
    assert save_res.status_code == 200

    saved_to = Path(save_res.json()["saved_to"])
    assert saved_to.is_file()
    saved = json.loads(saved_to.read_text())
    assert saved["title"] == plan_res.json()["title"]


def test_save_project_succeeds_even_though_continuity_failed(failing_continuity):
    """The requirement stated explicitly: Save must work when continuity is
    incomplete or failed, not only on the happy path."""
    plan_res = client.post("/api/plan", json={"concept": "A lighthouse keeper meets a sea spirit."})
    assert plan_res.status_code == 200
    session_id = plan_res.json()["session_id"]

    save_res = client.post(f"/api/session/{session_id}/save")
    assert save_res.status_code == 200

    saved = json.loads(Path(save_res.json()["saved_to"]).read_text())
    assert saved["title"] == plan_res.json()["title"]
    assert any(f["target"] == "project" for f in saved["render_plan"]["flags"])


def test_save_project_for_an_unknown_session_is_404():
    res = client.post("/api/session/does-not-exist/save")
    assert res.status_code == 404
    assert "error" in res.json()


def test_a_checkpoint_exists_on_disk_before_the_plan_response_is_even_returned(
    failing_continuity,
):
    """The persistence half of the fix, exercised through the real endpoint:
    by the time /api/plan responds, a checkpoint of the plan (written before
    continuity ran) is already on disk in the session's own directory —
    independent of the in-memory Project the response itself carries."""
    res = client.post("/api/plan", json={"concept": "A lighthouse keeper meets a sea spirit."})
    assert res.status_code == 200
    project = res.json()

    from moviecrew.portal.app import _sessions

    session = _sessions[project["session_id"]]
    checkpoint = Path(session.session_dir) / "project_checkpoint.json"
    assert checkpoint.is_file()
    checkpointed = json.loads(checkpoint.read_text())
    assert checkpointed["title"] == project["title"]
