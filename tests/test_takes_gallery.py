"""Tests for the portal's takes gallery endpoints.

Fully offline: takes are plain files under tmp_path and a "clip" is a few
bytes standing in for an MP4. The takes root is read per-request from the
environment, so monkeypatching it is enough to point the app at a fixture.

Skips cleanly when the test client isn't available (the `portal` extra is
optional) — guarded on TestClient itself, since starlette raises RuntimeError
rather than ImportError when its HTTP client is missing.
"""

from __future__ import annotations

import pytest

try:
    from fastapi.testclient import TestClient
except (ImportError, RuntimeError) as exc:
    pytest.skip(f"fastapi TestClient unavailable: {exc}", allow_module_level=True)

from moviecrew.portal.app import _TAKES_ROOT_ENV, app  # noqa: E402
from moviecrew.takes import Take, save_take  # noqa: E402

client = TestClient(app)

_MP4 = b"\x00\x00\x00\x18ftypisom" + b"\x00" * 32


@pytest.fixture()
def takes_root(tmp_path, monkeypatch):
    """An empty takes root the app will read for the duration of a test."""
    root = tmp_path / "takes"
    root.mkdir()
    monkeypatch.setenv(_TAKES_ROOT_ENV, str(root))
    return root


def _add_take(root, *, shot_id="sc1-sh1", scene_id="sc1", number=1, with_video=True, **kw):
    take = Take(
        shot_id=shot_id,
        scene_id=scene_id,
        take_number=number,
        video_path=f"{scene_id}/{shot_id}/take_{number:03d}.mp4",
        **kw,
    )
    save_take(take, root)
    if with_video:
        video = root / scene_id / shot_id / f"take_{number:03d}.mp4"
        video.write_bytes(_MP4)
    return take


# ---------------------------------------------------------------------- #
# Listing                                                                 #
# ---------------------------------------------------------------------- #


def test_takes_root_reported_by_health(takes_root):
    data = client.get("/api/health").json()
    assert data["takes_root"] == str(takes_root)
    assert data["takes_root_exists"] is True


def test_missing_takes_root_is_reported_not_an_error(tmp_path, monkeypatch):
    monkeypatch.setenv(_TAKES_ROOT_ENV, str(tmp_path / "nope"))
    res = client.get("/api/takes")
    assert res.status_code == 200
    body = res.json()
    assert body["takes_root_exists"] is False
    assert body["take_count"] == 0
    assert body["shots"] == {}


def test_empty_takes_root_lists_nothing(takes_root):
    body = client.get("/api/takes").json()
    assert body["take_count"] == 0
    assert body["shots"] == {}


def test_takes_are_grouped_by_shot(takes_root):
    _add_take(takes_root, shot_id="sc1-sh1", number=1)
    _add_take(takes_root, shot_id="sc1-sh1", number=2)
    _add_take(takes_root, shot_id="sc1-sh2", number=1)

    body = client.get("/api/takes").json()
    assert body["take_count"] == 3
    assert len(body["shots"]["sc1-sh1"]) == 2
    assert len(body["shots"]["sc1-sh2"]) == 1


def test_take_payload_carries_the_cinematography(takes_root):
    _add_take(
        takes_root,
        camera_move="slow dolly-in",
        lens="24mm",
        framing="wide, low angle",
        duration_s=8.0,
        fps=24,
        resolution="1920x1080",
        blocked_by="auto",
    )
    take = client.get("/api/takes").json()["shots"]["sc1-sh1"][0]

    assert take["take_id"] == "sc1-sh1#1"
    assert take["camera_move"] == "slow dolly-in"
    assert take["lens"] == "24mm"
    assert take["resolution"] == "1920x1080"
    assert take["blocked_by"] == "auto"
    assert take["has_video"] is True
    assert take["video_url"] == "/api/takes/sc1/sc1-sh1/1/video"


def test_take_without_a_clip_is_listed_but_flagged(takes_root):
    """A render that died still has a record; the gallery must show it as
    unplayable rather than omitting it."""
    _add_take(takes_root, with_video=False)
    take = client.get("/api/takes").json()["shots"]["sc1-sh1"][0]
    assert take["has_video"] is False


def test_takes_filter_by_shot(takes_root):
    _add_take(takes_root, shot_id="sc1-sh1")
    _add_take(takes_root, shot_id="sc1-sh2")

    body = client.get("/api/takes", params={"shot_id": "sc1-sh2"}).json()
    assert list(body["shots"]) == ["sc1-sh2"]


def test_takes_filter_by_scene(takes_root):
    _add_take(takes_root, scene_id="sc1", shot_id="sc1-sh1")
    _add_take(takes_root, scene_id="sc2", shot_id="sc2-sh1")

    body = client.get("/api/takes", params={"scene_id": "sc2"}).json()
    assert list(body["shots"]) == ["sc2-sh1"]


# ---------------------------------------------------------------------- #
# Video serving                                                           #
# ---------------------------------------------------------------------- #


def test_video_endpoint_serves_the_clip(takes_root):
    _add_take(takes_root)
    res = client.get("/api/takes/sc1/sc1-sh1/1/video")
    assert res.status_code == 200
    assert "video/mp4" in res.headers["content-type"]
    assert res.content == _MP4


def test_video_endpoint_supports_range_requests(takes_root):
    """The player seeks with Range; without 206 the whole clip is refetched."""
    _add_take(takes_root)
    res = client.get("/api/takes/sc1/sc1-sh1/1/video", headers={"Range": "bytes=0-7"})
    assert res.status_code == 206
    assert res.content == _MP4[:8]


def test_unknown_take_is_404(takes_root):
    _add_take(takes_root, number=1)
    res = client.get("/api/takes/sc1/sc1-sh1/99/video")
    assert res.status_code == 404
    assert "error" in res.json()


def test_record_without_a_file_is_404_not_a_crash(takes_root):
    _add_take(takes_root, with_video=False)
    res = client.get("/api/takes/sc1/sc1-sh1/1/video")
    assert res.status_code == 404
    assert "no video file" in res.json()["error"]


def test_video_for_wrong_scene_is_404(takes_root):
    _add_take(takes_root, scene_id="sc1", shot_id="sc1-sh1")
    assert client.get("/api/takes/sc2/sc1-sh1/1/video").status_code == 404


# ---------------------------------------------------------------------- #
# Containment                                                             #
# ---------------------------------------------------------------------- #


def test_take_pointing_outside_the_root_is_refused(takes_root, tmp_path):
    """A record's video_path is data on disk, so it must not be trusted to
    stay inside the root — a doctored one must not exfiltrate a file."""
    secret = tmp_path / "secret.mp4"
    secret.write_bytes(b"SECRET")

    take = Take(
        shot_id="sc1-sh1",
        scene_id="sc1",
        take_number=1,
        video_path=str(secret),  # absolute, outside the takes root
    )
    save_take(take, takes_root)

    res = client.get("/api/takes/sc1/sc1-sh1/1/video")
    assert res.status_code == 403
    assert res.content != b"SECRET"


def test_relative_escape_in_a_record_is_refused(takes_root, tmp_path):
    secret = tmp_path / "secret.mp4"
    secret.write_bytes(b"SECRET")

    take = Take(
        shot_id="sc1-sh1",
        scene_id="sc1",
        take_number=1,
        video_path="../secret.mp4",
    )
    save_take(take, takes_root)

    res = client.get("/api/takes/sc1/sc1-sh1/1/video")
    assert res.status_code == 403
    assert res.content != b"SECRET"


def test_traversal_in_the_url_does_not_reach_a_file(takes_root, tmp_path):
    """Nothing is ever built from the URL: the take must exist as a record."""
    (tmp_path / "secret.mp4").write_bytes(b"SECRET")
    res = client.get("/api/takes/..%2F..%2F..%2Ftmp/sh/1/video")
    assert res.status_code in (403, 404)
    assert b"SECRET" not in res.content


def test_takes_root_is_not_settable_from_a_request(takes_root, tmp_path):
    """Server-side config only — a query param must not redirect the root."""
    other = tmp_path / "elsewhere"
    (other / "sc9" / "sc9-sh1").mkdir(parents=True)
    _add_take(takes_root, shot_id="sc1-sh1")

    body = client.get("/api/takes", params={"takes_root": str(other)}).json()
    assert body["takes_root"] == str(takes_root)
    assert list(body["shots"]) == ["sc1-sh1"]
