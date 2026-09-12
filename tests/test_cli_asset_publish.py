"""cli._asset_publisher: the seam that makes GenerativeVideoBackend's
publish= actually work from the command line.

The CLI's `--video-backend openrouter` path used to build a
GenerativeVideoBackend with no publish= at all, so a chain could never
survive contact with a real hosted provider — regardless of whether an
asset store bucket was configured. Both halves existed and were each
independently correct (an asset store to publish to; a publish= seam that
uses one when given it), but nothing actually connected them. This file is
the coverage for that connection: with no bucket, chaining stays safely
disabled; with one, a multi-shot take actually survives the round trip
through a hosted provider.
"""

from __future__ import annotations

import pytest

from moviecrew.assets import AssetError, S3AssetStore
from moviecrew.cli import _asset_publisher, _build_video_backend
from moviecrew.crew import MovieCrew
from moviecrew.generative import GenerativeVideoBackend
from moviecrew.mock import MockLLMClient
from moviecrew.schema import Bible, Project, RenderPlan, Scene, Shot

_ENV_VARS = (
    "MOVIECREW_S3_BUCKET",
    "MOVIECREW_S3_ENDPOINT",
    "MOVIECREW_S3_ACCESS_KEY",
    "MOVIECREW_S3_SECRET_KEY",
    "MOVIECREW_S3_REGION",
    "MOVIECREW_ASSET_BASE_URL",
)


@pytest.fixture(autouse=True)
def no_real_bucket(monkeypatch):
    """The default state this whole codebase assumes: no credentials, so
    nothing here can accidentally reach a real network or bucket."""
    for var in _ENV_VARS:
        monkeypatch.delenv(var, raising=False)


class _FakeTransport:
    """Stands in for the real network call `S3AssetStore` would otherwise
    make, so the test proves the wiring without touching the internet."""

    def __init__(self):
        self.calls: list[dict] = []

    def __call__(self, method, url, headers, body):
        self.calls.append({"method": method, "url": url, "headers": headers, "body": body})
        return b""


def _project(shots: list[Shot], chain: list[str]) -> Project:
    scene = Scene(id="sc1", slug="s", title="t", summary="s", shots=shots)
    return Project(
        title="t",
        logline="l",
        bible=Bible(style="s", palette="p", mood="m"),
        scenes=[scene],
        render_plan=RenderPlan(order=[s.id for s in shots], chains=[chain]),
    )


# ---------------------------------------------------------------------- #
# The gap, confirmed                                                       #
# ---------------------------------------------------------------------- #


def test_the_openrouter_cli_backend_has_no_publisher_with_no_bucket_configured(
    tmp_path, monkeypatch
):
    """Exactly the state flagged in both PR bodies: with nothing configured,
    the CLI's openrouter backend cannot chain, because it has no way to
    deliver a clip back to the provider that generated it."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")
    backend = _build_video_backend(
        "openrouter", model="m", out_dir=str(tmp_path), resolution="720p"
    )
    assert isinstance(backend, GenerativeVideoBackend)
    assert backend._publish is None


def test_a_chain_through_the_cli_openrouter_backend_segments_with_no_bucket(
    tmp_path, monkeypatch
):
    """The safe default in the absence of a fix: no bucket, no continuity —
    every shot renders standalone rather than risk a paid continuation
    against an unreachable URL."""
    from moviecrew.render import FakeRenderClient, RenderCapabilities

    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")

    class _Client(FakeRenderClient):
        def capabilities(self, model=None):
            return RenderCapabilities(max_duration_s=10, supports_video_reference=True)

    backend = _build_video_backend(
        "openrouter", model="m", out_dir=str(tmp_path), resolution="720p"
    )
    backend.client = _Client()  # swap in a controllable capability, keep publish=None

    assert backend.segment(["s0", "s1", "s2"]) == [["s0"], ["s1"], ["s2"]]


# ---------------------------------------------------------------------- #
# _asset_publisher: the fix                                                #
# ---------------------------------------------------------------------- #


def test_asset_publisher_is_none_without_a_bucket(tmp_path):
    assert _asset_publisher(str(tmp_path)) is None


def test_asset_publisher_is_none_with_a_bucket_but_no_public_base(
    tmp_path, monkeypatch
):
    """A private bucket cannot serve a reference either — same rule
    put_reachable already enforces, reached through a different door."""
    monkeypatch.setenv("MOVIECREW_S3_BUCKET", "films")
    monkeypatch.setenv("MOVIECREW_S3_ENDPOINT", "https://acct.r2.cloudflarestorage.com")
    monkeypatch.setenv("MOVIECREW_S3_ACCESS_KEY", "AK")
    monkeypatch.setenv("MOVIECREW_S3_SECRET_KEY", "SK")
    assert _asset_publisher(str(tmp_path)) is None


def test_asset_publisher_uploads_the_local_file_and_returns_a_public_url(
    tmp_path, monkeypatch
):
    monkeypatch.setenv("MOVIECREW_S3_BUCKET", "films")
    monkeypatch.setenv("MOVIECREW_S3_ENDPOINT", "https://acct.r2.cloudflarestorage.com")
    monkeypatch.setenv("MOVIECREW_S3_ACCESS_KEY", "AK")
    monkeypatch.setenv("MOVIECREW_S3_SECRET_KEY", "SK")
    monkeypatch.setenv("MOVIECREW_ASSET_BASE_URL", "https://pub-abc.r2.dev")

    transport = _FakeTransport()
    monkeypatch.setattr("moviecrew.assets._urlopen_transport", transport)

    clip = tmp_path / "s0.mp4"
    clip.write_bytes(b"\x00\x00\x00\x18ftypisom")

    publish = _asset_publisher(str(tmp_path))
    assert publish is not None

    url = publish("s0", str(clip))

    assert url == "https://pub-abc.r2.dev/renders/s0.mp4"
    assert transport.calls[0]["method"] == "PUT"
    assert transport.calls[0]["headers"]["content-type"] == "video/mp4"


def test_asset_publisher_refuses_rather_than_silently_upload_when_unreachable(
    tmp_path, monkeypatch
):
    """put_reachable's own guarantee, inherited: a bucket that stops being
    reachable between the capability check and the actual PUT still fails
    loudly rather than handing back a URL a provider cannot use."""
    store = S3AssetStore(
        bucket="films",
        endpoint="https://acct.r2.cloudflarestorage.com",
        access_key="AK",
        secret_key="SK",
        public_base="",  # unreachable by construction
        transport=_FakeTransport(),
    )
    clip = tmp_path / "s0.mp4"
    clip.write_bytes(b"\x00\x00\x00\x18ftypisom")
    with pytest.raises(AssetError, match="reachable"):
        store.put_reachable(str(clip), "renders/s0.mp4")


# ---------------------------------------------------------------------- #
# End to end: a chain actually survives once a bucket is configured        #
# ---------------------------------------------------------------------- #


def test_a_two_shot_chain_stays_continuous_once_a_bucket_is_configured(
    tmp_path, monkeypatch
):
    """The thing that could not be tested before: with the asset store
    wired as publish=, a chain that a hosted model can drive from a video
    reference actually stays a chain end to end through the CLI's factory —
    not just inside GenerativeVideoBackend's own unit tests, which always
    injected a publisher by hand."""
    from moviecrew.render import FakeRenderClient, RenderCapabilities

    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")
    monkeypatch.setenv("MOVIECREW_S3_BUCKET", "films")
    monkeypatch.setenv("MOVIECREW_S3_ENDPOINT", "https://acct.r2.cloudflarestorage.com")
    monkeypatch.setenv("MOVIECREW_S3_ACCESS_KEY", "AK")
    monkeypatch.setenv("MOVIECREW_S3_SECRET_KEY", "SK")
    monkeypatch.setenv("MOVIECREW_ASSET_BASE_URL", "https://pub-abc.r2.dev")
    monkeypatch.setattr("moviecrew.assets._urlopen_transport", _FakeTransport())

    class _Client(FakeRenderClient):
        def capabilities(self, model=None):
            return RenderCapabilities(max_duration_s=10, supports_video_reference=True)

    backend = _build_video_backend(
        "openrouter", model="m", out_dir=str(tmp_path), resolution="720p"
    )
    backend.client = _Client()
    backend.poll_interval_s = 0
    backend._sleep = lambda _: None

    assert backend._publish is not None
    assert backend.can_chain is True
    assert backend.segment(["s0", "s1", "s2"]) == [["s0", "s1", "s2"]]

    shots = [
        Shot(id=f"s{i}", scene_id="sc1", description="d", duration_s=6)
        for i in range(3)
    ]
    project = _project(shots, [shot.id for shot in shots])

    results = MovieCrew(MockLLMClient()).render(project, backend)

    assert [r.status for r in results] == ["succeeded"] * 3
    # Each continuation was actually driven by the rehosted clip, not the
    # provider's own (never-published) result URL.
    submitted = [spec for spec, _model in backend.client.submitted]
    assert submitted[0].reference_video is None
    assert submitted[1].reference_video == "https://pub-abc.r2.dev/renders/s0.mp4"
    assert submitted[2].reference_video == "https://pub-abc.r2.dev/renders/s1.mp4"
