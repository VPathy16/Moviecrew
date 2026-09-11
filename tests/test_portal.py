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

import pytest

try:
    from fastapi.testclient import TestClient
except (ImportError, RuntimeError) as exc:
    pytest.skip(f"fastapi TestClient unavailable: {exc}", allow_module_level=True)

from moviecrew.portal.app import app  # noqa: E402

client = TestClient(app)


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
