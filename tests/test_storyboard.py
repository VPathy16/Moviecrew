"""Tests for the STORYBOARD gate in the studio session state machine.

Fully offline: uses MockLLMClient (no network) and MockImageProvider (no
image API).  The portal storyboard endpoints are exercised through
fastapi.testclient.TestClient; those tests skip cleanly when fastapi isn't
installed.
"""

from __future__ import annotations

import pytest

from moviecrew.crew import MovieCrew
from moviecrew.image import ImageProvider, MockImageProvider
from moviecrew.mock import MockLLMClient
from moviecrew.studio import Stage, StudioSession


# ---------------------------------------------------------------------- #
# Shared fixtures                                                         #
# ---------------------------------------------------------------------- #


@pytest.fixture()
def project(tmp_path):
    crew = MovieCrew(MockLLMClient())
    return crew.make("A lighthouse keeper and a sea spirit.")


@pytest.fixture()
def session(project, tmp_path):
    return StudioSession(
        session_id="test-session",
        stage=Stage.SHOT_DEFS,
        project=project,
        session_dir=str(tmp_path),
        image_provider=MockImageProvider(),
    )


# ---------------------------------------------------------------------- #
# Core state-machine tests                                                #
# ---------------------------------------------------------------------- #


def test_board_has_one_frame_per_shot(session):
    session.produce()
    all_shots = [shot for scene in session.project.scenes for shot in scene.shots]
    assert len(session.board) == len(all_shots)
    for frame in session.board:
        assert frame.shot_id
        assert frame.prompt_used
        assert frame.status in ("ok", "failed")


def test_all_mock_frames_are_ok_with_image_path(session):
    session.produce()
    for frame in session.board:
        assert frame.status == "ok"
        assert frame.image_path is not None


def test_image_written_to_session_storyboard_dir(session):
    from pathlib import Path

    session.produce()
    for frame in session.board:
        assert frame.image_path is not None
        assert Path(frame.image_path).exists()


def test_provider_failure_yields_failed_frame_without_aborting(session):
    class AlwaysFail(ImageProvider):
        def generate(self, prompt: str, shot_id: str) -> bytes:
            raise RuntimeError("API down")

    session.image_provider = AlwaysFail()
    session.produce()

    all_shots = [s for scene in session.project.scenes for s in scene.shots]
    assert len(session.board) == len(all_shots)
    for frame in session.board:
        assert frame.status == "failed"
        assert frame.image_path is None


def test_produce_transitions_stage_to_storyboard(session):
    assert session.stage == Stage.SHOT_DEFS
    session.produce()
    assert session.stage == Stage.STORYBOARD


def test_approve_promotes_anchored_frames_and_advances_to_output(session):
    session.produce()

    anchored = session.project.scenes[0].shots[0]
    anchored.consistency_anchor = True

    ok_frame = next(f for f in session.board if f.shot_id == anchored.id)
    assert ok_frame.status == "ok"

    session.approve()

    assert session.stage == Stage.OUTPUT
    assert anchored.reference_image_ids == [ok_frame.image_path]


def test_approve_does_not_promote_failed_frames(session):
    class AlwaysFail(ImageProvider):
        def generate(self, prompt: str, shot_id: str) -> bytes:
            raise RuntimeError("fail")

    session.image_provider = AlwaysFail()
    session.produce()

    anchored = session.project.scenes[0].shots[0]
    anchored.consistency_anchor = True
    original_refs = list(anchored.reference_image_ids)

    session.approve()

    assert session.stage == Stage.OUTPUT
    assert anchored.reference_image_ids == original_refs


def test_approve_leaves_non_anchor_shots_unchanged(session):
    session.produce()

    shot = session.project.scenes[0].shots[0]
    shot.consistency_anchor = False
    original_refs = list(shot.reference_image_ids)

    session.approve()

    assert shot.reference_image_ids == original_refs


def test_revise_single_frame_clears_promoted_reference(session):
    session.produce()

    anchored = session.project.scenes[0].shots[0]
    anchored.consistency_anchor = True
    session.approve()

    assert session.stage == Stage.OUTPUT
    assert anchored.reference_image_ids  # was promoted

    session.revise(shot_id=anchored.id)

    assert anchored.reference_image_ids == []
    assert session.stage == Stage.STORYBOARD


def test_revise_single_frame_does_not_clear_other_shots(session):
    session.produce()

    shots = [s for scene in session.project.scenes for s in scene.shots]
    if len(shots) < 2:
        pytest.skip("need at least 2 shots for this test")

    shots[0].consistency_anchor = True
    shots[1].consistency_anchor = True
    session.approve()

    promoted_second = list(shots[1].reference_image_ids)
    session.revise(shot_id=shots[0].id)

    assert shots[0].reference_image_ids == []
    assert shots[1].reference_image_ids == promoted_second


def test_revise_whole_board_regenerates_all_frames(session):
    session.produce()
    count_before = len(session.board)

    session.revise()  # no shot_id -> whole board

    assert len(session.board) == count_before
    assert session.stage == Stage.STORYBOARD


def test_revise_whole_board_clears_all_promoted_refs(session):
    session.produce()
    shots = [s for scene in session.project.scenes for s in scene.shots]
    for shot in shots:
        shot.consistency_anchor = True
    session.approve()

    session.revise()  # regenerate everything

    for shot in shots:
        assert shot.reference_image_ids == []


def test_still_prompt_strips_camera_sentences():
    from moviecrew.studio import _veo_to_still_prompt

    veo = (
        "Mara grips a rope rail and hauls herself up the cliff. "
        "Camera tracks low and close, drifting upward. "
        "Cold storm light rakes in from the horizon. "
        "Wind roars, waves crash."
    )
    still = _veo_to_still_prompt(veo)
    assert "Still frame:" in still
    assert "Camera tracks" not in still


def test_still_prompt_keeps_subject_and_light():
    from moviecrew.studio import _veo_to_still_prompt

    veo = (
        "Mara grips a rope rail. "
        "Camera tracks low. "
        "Cold blue-grey storm light rakes in. "
        "Shot on a 24mm lens."
    )
    still = _veo_to_still_prompt(veo)
    assert "Mara" in still
    assert "storm light" in still


# ---------------------------------------------------------------------- #
# Portal storyboard endpoint tests                                        #
# ---------------------------------------------------------------------- #


pytest.importorskip("fastapi")

from fastapi.testclient import TestClient  # noqa: E402

from moviecrew.portal.app import _sessions, app  # noqa: E402

client = TestClient(app)


def _fresh_session_id() -> str:
    """POST /api/plan with the mock backend and return the session_id."""
    res = client.post("/api/plan", json={"concept": "A lighthouse and a sea spirit."})
    assert res.status_code == 200
    sid = res.json().get("session_id")
    assert sid, "plan response must include session_id"
    return sid


def test_plan_includes_session_id_and_stage():
    res = client.post("/api/plan", json={"concept": "test concept"})
    assert res.status_code == 200
    data = res.json()
    assert "session_id" in data
    assert data["stage"] == "shot_defs"
    assert data["title"]


def test_storyboard_generate_returns_one_frame_per_shot():
    sid = _fresh_session_id()
    res = client.post("/api/storyboard", json={"session_id": sid})
    assert res.status_code == 200
    data = res.json()
    assert data["stage"] == "storyboard"
    frames = data["frames"]
    assert frames

    session = _sessions[sid]
    all_shots = [s for scene in session.project.scenes for s in scene.shots]
    assert len(frames) == len(all_shots)
    for frame in frames:
        assert frame["shot_id"]
        assert frame["status"] in ("ok", "failed")


def test_storyboard_image_endpoint_serves_png():
    sid = _fresh_session_id()
    client.post("/api/storyboard", json={"session_id": sid})
    session = _sessions[sid]
    ok_frame = next((f for f in session.board if f.status == "ok"), None)
    if ok_frame is None:
        pytest.skip("no successful frame")
    res = client.get(f"/api/storyboard/{sid}/{ok_frame.shot_id}")
    assert res.status_code == 200
    assert "image/png" in res.headers["content-type"]


def test_storyboard_approve_advances_stage():
    sid = _fresh_session_id()
    client.post("/api/storyboard", json={"session_id": sid})
    res = client.post("/api/storyboard/approve", json={"session_id": sid})
    assert res.status_code == 200
    assert res.json()["stage"] == "output"


def test_storyboard_regenerate_returns_single_frame():
    sid = _fresh_session_id()
    client.post("/api/storyboard", json={"session_id": sid})
    session = _sessions[sid]
    shot_id = session.board[0].shot_id

    res = client.post(
        "/api/storyboard/regenerate",
        json={"session_id": sid, "shot_id": shot_id, "feedback": "darker tone"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["frame"]["shot_id"] == shot_id
    assert data["stage"] == "storyboard"


def test_storyboard_unknown_session_returns_404():
    res = client.post("/api/storyboard", json={"session_id": "does-not-exist"})
    assert res.status_code == 404
    assert "error" in res.json()


def test_storyboard_approve_unknown_session_returns_404():
    res = client.post("/api/storyboard/approve", json={"session_id": "does-not-exist"})
    assert res.status_code == 404
