"""Tests for the portal's generated-renders gallery.

Fully offline: a "render" is a few bytes standing in for an MP4, written
where the render path says it belongs. The takes root is read per-request
from the environment, so monkeypatching it points the app at a fixture.

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

from moviecrew.portal.app import _TAKES_ROOT_ENV, app, render_path  # noqa: E402
from moviecrew.takes import Take, save_take  # noqa: E402

client = TestClient(app)

_MP4 = b"\x00\x00\x00\x18ftypisom" + b"\x00" * 32


@pytest.fixture()
def takes_root(tmp_path, monkeypatch):
    root = tmp_path / "takes"
    root.mkdir()
    monkeypatch.setenv(_TAKES_ROOT_ENV, str(root))
    return root


def _add_take(root, *, shot_id="sc1-sh1", scene_id="sc1", number=1, renders=()):
    take = Take(
        shot_id=shot_id,
        scene_id=scene_id,
        take_number=number,
        video_path=f"{scene_id}/{shot_id}/take_{number:03d}.mp4",
        renders=list(renders),
    )
    save_take(take, root)
    video = root / scene_id / shot_id / f"take_{number:03d}.mp4"
    video.write_bytes(_MP4)
    return take


def _add_render(root, take, job_id, payload=_MP4):
    path = render_path(root, take.scene_id, take.shot_id, job_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return path


# ---------------------------------------------------------------------- #
# Listing                                                                 #
# ---------------------------------------------------------------------- #


def test_no_renders_lists_nothing(takes_root):
    _add_take(takes_root)
    body = client.get("/api/renders").json()
    assert body["render_count"] == 0
    assert body["shots"] == {}


def test_render_is_listed_against_its_take(takes_root):
    take = _add_take(takes_root, renders=["job-a"])
    _add_render(takes_root, take, "job-a")

    body = client.get("/api/renders").json()
    assert body["render_count"] == 1
    entry = body["shots"]["sc1-sh1"][0]
    assert entry["job_id"] == "job-a"
    assert entry["take_id"] == "sc1-sh1#1"
    assert entry["take_number"] == 1
    assert entry["size_bytes"] == len(_MP4)
    assert entry["video_url"] == "/api/renders/sc1/sc1-sh1/job-a/video"
    assert entry["take_video_url"] == "/api/takes/sc1/sc1-sh1/1/video"


def test_renders_are_grouped_by_shot(takes_root):
    a = _add_take(takes_root, shot_id="sc1-sh1")
    b = _add_take(takes_root, shot_id="sc1-sh2")
    _add_render(takes_root, a, "job-a")
    _add_render(takes_root, a, "job-b")
    _add_render(takes_root, b, "job-c")

    body = client.get("/api/renders").json()
    assert body["render_count"] == 3
    assert len(body["shots"]["sc1-sh1"]) == 2
    assert len(body["shots"]["sc1-sh2"]) == 1


def test_render_without_lineage_is_listed_and_flagged(takes_root):
    """A render that finished while the portal was restarting has no entry in
    take.renders. It cost money, so it must still appear — flagged, not lost."""
    take = _add_take(takes_root, renders=[])
    _add_render(takes_root, take, "orphan-job")

    entry = client.get("/api/renders").json()["shots"]["sc1-sh1"][0]
    assert entry["job_id"] == "orphan-job"
    assert entry["linked"] is False


def test_linked_flag_is_true_when_the_record_knows(takes_root):
    take = _add_take(takes_root, renders=["job-a"])
    _add_render(takes_root, take, "job-a")
    entry = client.get("/api/renders").json()["shots"]["sc1-sh1"][0]
    assert entry["linked"] is True


def test_renders_filter_by_shot(takes_root):
    a = _add_take(takes_root, shot_id="sc1-sh1")
    b = _add_take(takes_root, shot_id="sc1-sh2")
    _add_render(takes_root, a, "job-a")
    _add_render(takes_root, b, "job-b")

    body = client.get("/api/renders", params={"shot_id": "sc1-sh2"}).json()
    assert list(body["shots"]) == ["sc1-sh2"]


# ---------------------------------------------------------------------- #
# Serving                                                                 #
# ---------------------------------------------------------------------- #


def test_render_video_is_served(takes_root):
    take = _add_take(takes_root)
    _add_render(takes_root, take, "job-a")

    res = client.get("/api/renders/sc1/sc1-sh1/job-a/video")
    assert res.status_code == 200
    assert "video/mp4" in res.headers["content-type"]
    assert res.content == _MP4


def test_render_video_supports_range_requests(takes_root):
    take = _add_take(takes_root)
    _add_render(takes_root, take, "job-a")

    res = client.get(
        "/api/renders/sc1/sc1-sh1/job-a/video", headers={"Range": "bytes=0-7"}
    )
    assert res.status_code == 206
    assert res.content == _MP4[:8]


def test_download_flag_sets_an_attachment_header(takes_root):
    take = _add_take(takes_root)
    _add_render(takes_root, take, "job-a")

    res = client.get("/api/renders/sc1/sc1-sh1/job-a/video", params={"download": "true"})
    assert res.status_code == 200
    assert "attachment" in res.headers["content-disposition"]
    assert "sc1-sh1_job-a.mp4" in res.headers["content-disposition"]


def test_unknown_render_is_404(takes_root):
    _add_take(takes_root)
    res = client.get("/api/renders/sc1/sc1-sh1/nope/video")
    assert res.status_code == 404
    assert "error" in res.json()


# ---------------------------------------------------------------------- #
# The whole arc                                                           #
# ---------------------------------------------------------------------- #


def test_generate_stores_and_the_gallery_serves_it(takes_root, monkeypatch):
    """Take -> generate -> stored -> listed -> playable -> downloadable.

    Runs on FakeRenderClient (no key, no spend), which is the point: the arc
    is exercisable offline end to end, so a break shows up here rather than
    on a paid render.
    """
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    # The fake backend advertises video-reference support, so the portal
    # rightly refuses to submit without an address a provider could fetch
    # the take from. Give it one.
    monkeypatch.setenv("MOVIECREW_PUBLIC_BASE_URL", "https://previz.example.test")
    _add_take(takes_root)

    assert client.get("/api/renders").json()["render_count"] == 0

    submitted = client.post(
        "/api/render",
        json={
            "scene_id": "sc1",
            "shot_id": "sc1-sh1",
            "take_number": 1,
            "prompt": "a lone figure on a wet street",
        },
    ).json()
    job_id = submitted["job_id"]

    polled = client.get(f"/api/render/{job_id}").json()
    assert polled["status"] == "succeeded"
    assert polled["local_path"], "a finished render must be saved locally"
    assert polled["render_url"] == f"/api/renders/sc1/sc1-sh1/{job_id}/video"

    listing = client.get("/api/renders").json()
    assert listing["render_count"] == 1
    entry = listing["shots"]["sc1-sh1"][0]
    assert entry["job_id"] == job_id
    assert entry["linked"] is True, "the take record must know its render"

    played = client.get(polled["render_url"])
    assert played.status_code == 200
    assert "video/mp4" in played.headers["content-type"]

    downloaded = client.get(polled["render_url"], params={"download": "true"})
    assert "attachment" in downloaded.headers["content-disposition"]


# ---------------------------------------------------------------------- #
# Containment                                                             #
# ---------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "job_id",
    ["../../secret", "..%2F..%2Fsecret", "a/b", "", "job id", "-leading-dash"],
)
def test_malformed_job_ids_never_become_paths(takes_root, job_id):
    """The id is held to an id shape before it is joined to a path, so a
    traversal is refused by pattern rather than by luck of resolution."""
    res = client.get(f"/api/renders/sc1/sc1-sh1/{job_id}/video")
    assert res.status_code in (400, 404, 307)
    assert b"SECRET" not in res.content


def test_symlinked_render_outside_the_root_is_refused(takes_root, tmp_path):
    """The pattern check stops traversal; this check stops a symlink out."""
    secret = tmp_path / "secret.mp4"
    secret.write_bytes(b"SECRET")

    take = _add_take(takes_root)
    link = render_path(takes_root, take.scene_id, take.shot_id, "sneaky")
    link.parent.mkdir(parents=True, exist_ok=True)
    try:
        link.symlink_to(secret)
    except OSError:  # pragma: no cover - platform without symlink permission
        pytest.skip("symlinks unavailable")

    res = client.get("/api/renders/sc1/sc1-sh1/sneaky/video")
    assert res.status_code == 403
    assert res.content != b"SECRET"
