"""Tests for the optional FastAPI portal (the PLAN path only).

Fully offline: uses fastapi.testclient.TestClient and the mock LLM backend,
no network and no real API key needed. Skips cleanly if fastapi isn't
installed (the `portal` extra is optional).
"""

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient  # noqa: E402

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
    assert render_plan["prompts"]
    assert render_plan["chains"]
    assert render_plan["order"]

    for prompt in render_plan["prompts"]:
        assert prompt["prompt"]
        assert "negative_prompt" in prompt
        assert prompt["aspect_ratio"] == "16:9"


def test_plan_with_explicit_detail_level():
    res = client.post(
        "/api/plan", json={"concept": "A heist at a museum.", "backend": "mock", "detail": "lean"}
    )
    assert res.status_code == 200
    assert res.json()["render_plan"]["prompts"]


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
