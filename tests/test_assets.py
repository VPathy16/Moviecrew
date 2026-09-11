"""Tests for the asset store.

Fully offline: the local store is real filesystem work, and the S3 store
takes an injectable transport so signing and request shape are exercised
with no bucket, no credentials and no network.

The content-type tests are the load-bearing ones. A reference served as
application/octet-stream is silently ignored by at least one video backend —
the render succeeds, bills in full, and never looks at the file. That cost
four paid renders before anyone checked a header.
"""

from __future__ import annotations

import pytest

from moviecrew.assets import (
    Asset,
    AssetError,
    AssetStore,
    LocalAssetStore,
    S3AssetStore,
    build_asset_store,
    content_type_for,
    is_reachable,
    sigv4_headers,
    signing_key,
)


@pytest.fixture()
def clip(tmp_path):
    p = tmp_path / "take_001.mp4"
    p.write_bytes(b"\x00\x00\x00\x18ftypisom" + b"\x00" * 64)
    return str(p)


@pytest.fixture()
def still(tmp_path):
    p = tmp_path / "board.png"
    p.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 32)
    return str(p)


# ---------------------------------------------------------------------- #
# Content types                                                           #
# ---------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "name,expected",
    [
        ("a.mp4", "video/mp4"),
        ("a.MP4", "video/mp4"),
        ("a.mov", "video/quicktime"),
        ("a.png", "image/png"),
        ("a.jpg", "image/jpeg"),
        ("a.jpeg", "image/jpeg"),
        ("a.webp", "image/webp"),
    ],
)
def test_known_media_types_are_explicit(name, expected):
    assert content_type_for(name) == expected


def test_an_untypeable_file_is_refused_rather_than_stored_as_octet_stream():
    with pytest.raises(AssetError, match="octet-stream"):
        content_type_for("mystery.qqq")


def test_the_refusal_names_the_file():
    with pytest.raises(AssetError, match="mystery.qqq"):
        content_type_for("mystery.qqq")


# ---------------------------------------------------------------------- #
# Reachability                                                            #
# ---------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost:8000/x.mp4",
        "http://127.0.0.1:8000/x.mp4",
        "https://0.0.0.0/x.mp4",
        "http://[::1]:9/x.mp4",
        "",
        "/relative/path.mp4",
        "file:///tmp/x.mp4",
    ],
)
def test_addresses_a_provider_cannot_fetch(url):
    """A provider resolving 127.0.0.1 reaches its own machine, not ours."""
    assert is_reachable(url) is False


@pytest.mark.parametrize(
    "url",
    ["https://cdn.example.com/x.mp4", "https://x.trycloudflare.com/a.png", "http://10.0.0.4/x.mp4"],
)
def test_addresses_a_provider_can_fetch(url):
    assert is_reachable(url) is True


# ---------------------------------------------------------------------- #
# LocalAssetStore                                                         #
# ---------------------------------------------------------------------- #


def test_local_put_copies_and_types(tmp_path, clip):
    store = LocalAssetStore(str(tmp_path / "assets"))
    asset = store.put(clip, "takes/sc1/sc1-sh1/take_001.mp4")

    assert asset.content_type == "video/mp4"
    assert asset.size_bytes > 0
    assert (tmp_path / "assets/takes/sc1/sc1-sh1/take_001.mp4").is_file()


def test_local_url_is_none_without_a_base(tmp_path, clip):
    store = LocalAssetStore(str(tmp_path / "assets"))
    assert store.put(clip, "a.mp4").url is None
    assert store.serves_public_urls is False


def test_local_url_uses_the_base(tmp_path, clip):
    store = LocalAssetStore(str(tmp_path / "assets"), base_url="https://cdn.example.com/media")
    asset = store.put(clip, "takes/a.mp4")
    assert asset.url == "https://cdn.example.com/media/takes/a.mp4"
    assert store.serves_public_urls is True


def test_local_loopback_base_is_not_public(tmp_path):
    store = LocalAssetStore(str(tmp_path), base_url="http://127.0.0.1:8000")
    assert store.serves_public_urls is False


def test_local_round_trip(tmp_path, clip):
    store = LocalAssetStore(str(tmp_path / "assets"))
    store.put(clip, "a.mp4")
    out = store.get("a.mp4", str(tmp_path / "back.mp4"))
    assert out and open(out, "rb").read() == open(clip, "rb").read()


def test_local_get_of_a_missing_key_is_none(tmp_path):
    assert LocalAssetStore(str(tmp_path)).get("nope.mp4", str(tmp_path / "x.mp4")) is None


def test_local_delete(tmp_path, clip):
    store = LocalAssetStore(str(tmp_path / "assets"))
    store.put(clip, "a.mp4")
    assert store.delete("a.mp4") is True
    assert store.delete("a.mp4") is False


@pytest.mark.parametrize("key", ["../escape.mp4", "a/../../escape.mp4"])
def test_local_refuses_a_key_that_escapes_the_root(tmp_path, clip, key):
    store = LocalAssetStore(str(tmp_path / "assets"))
    with pytest.raises(AssetError, match="outside"):
        store.put(clip, key)


# ---------------------------------------------------------------------- #
# put_reachable                                                           #
# ---------------------------------------------------------------------- #


def test_put_reachable_refuses_an_unusable_address(tmp_path, clip):
    """Fails before the render request rather than after the provider has
    tried and failed to fetch the file."""
    store = LocalAssetStore(str(tmp_path), base_url="http://localhost:8000")
    with pytest.raises(AssetError, match="reachable"):
        store.put_reachable(clip, "a.mp4")


def test_put_reachable_passes_a_usable_one(tmp_path, clip):
    store = LocalAssetStore(str(tmp_path), base_url="https://cdn.example.com")
    assert store.put_reachable(clip, "a.mp4").url == "https://cdn.example.com/a.mp4"


# ---------------------------------------------------------------------- #
# SigV4                                                                   #
# ---------------------------------------------------------------------- #


def test_signing_key_is_deterministic():
    a = signing_key("secret", "20260911", "auto", "s3")
    b = signing_key("secret", "20260911", "auto", "s3")
    assert a == b and len(a) == 32


def test_signing_key_changes_with_every_input():
    base = signing_key("secret", "20260911", "auto", "s3")
    assert signing_key("other", "20260911", "auto", "s3") != base
    assert signing_key("secret", "20260912", "auto", "s3") != base
    assert signing_key("secret", "20260911", "us-east-1", "s3") != base


def test_sigv4_headers_carry_the_required_fields():
    h = sigv4_headers(
        method="PUT",
        url="https://acct.r2.cloudflarestorage.com/bucket/takes/a.mp4",
        payload=b"data",
        access_key="AK",
        secret_key="SK",
        region="auto",
        extra_headers={"content-type": "video/mp4"},
    )
    assert h["Authorization"].startswith("AWS4-HMAC-SHA256 Credential=AK/")
    assert "SignedHeaders=" in h["Authorization"]
    assert h["host"] == "acct.r2.cloudflarestorage.com"
    assert h["x-amz-content-sha256"] == (
        "3a6eb0790f39ac87c94f3856b2dd2c5d110e6811602261a9a923d3bb23adc8b7"  # sha256("data")
    )


def test_signed_headers_include_content_type_when_given():
    h = sigv4_headers(
        method="PUT",
        url="https://x.example.com/b/k",
        payload=b"",
        access_key="AK",
        secret_key="SK",
        region="auto",
        extra_headers={"content-type": "image/png"},
    )
    assert "content-type" in h["Authorization"]
    assert h["content-type"] == "image/png"


def test_the_signature_covers_the_payload():
    def sign(payload):
        return sigv4_headers(
            method="PUT",
            url="https://x.example.com/b/k",
            payload=payload,
            access_key="AK",
            secret_key="SK",
            region="auto",
        )["Authorization"]

    assert sign(b"one") != sign(b"two")


# ---------------------------------------------------------------------- #
# S3AssetStore                                                            #
# ---------------------------------------------------------------------- #


class _Transport:
    def __init__(self, payload=b""):
        self.calls = []
        self.payload = payload

    def __call__(self, method, url, headers, body):
        self.calls.append({"method": method, "url": url, "headers": headers, "body": body})
        return self.payload


def _s3(transport, **kw):
    return S3AssetStore(
        bucket="films",
        endpoint="https://acct.r2.cloudflarestorage.com",
        access_key="AK",
        secret_key="SK",
        transport=transport,
        **kw,
    )


def test_s3_put_sends_a_signed_put_with_the_right_type(clip):
    t = _Transport()
    asset = _s3(t).put(clip, "takes/sc1/take_001.mp4")

    call = t.calls[0]
    assert call["method"] == "PUT"
    assert call["url"] == (
        "https://acct.r2.cloudflarestorage.com/films/takes/sc1/take_001.mp4"
    )
    assert call["headers"]["content-type"] == "video/mp4"
    assert "Authorization" in call["headers"]
    assert asset.content_type == "video/mp4"


def test_s3_url_is_none_without_a_public_base(clip):
    assert _s3(_Transport()).put(clip, "a.mp4").url is None


def test_s3_url_uses_the_public_base(clip):
    store = _s3(_Transport(), public_base="https://media.example.com")
    assert store.put(clip, "takes/a.mp4").url == "https://media.example.com/takes/a.mp4"
    assert store.serves_public_urls is True


def test_s3_private_bucket_cannot_serve_a_reference(clip):
    """The correct answer for a bucket with no public address."""
    with pytest.raises(AssetError, match="reachable"):
        _s3(_Transport()).put_reachable(clip, "a.mp4")


def test_s3_get_writes_the_body(tmp_path):
    t = _Transport(payload=b"bytes-back")
    out = _s3(t).get("a.mp4", str(tmp_path / "out.mp4"))
    assert out and open(out, "rb").read() == b"bytes-back"
    assert t.calls[0]["method"] == "GET"


def test_s3_get_of_a_missing_key_is_none(tmp_path):
    def fails(*a, **k):
        raise AssetError("404")

    assert _s3(fails).get("nope.mp4", str(tmp_path / "x")) is None


def test_s3_delete(tmp_path):
    t = _Transport()
    assert _s3(t).delete("a.mp4") is True
    assert t.calls[0]["method"] == "DELETE"


def test_s3_refuses_an_untypeable_file(tmp_path):
    odd = tmp_path / "thing.qqq"
    odd.write_bytes(b"x")
    with pytest.raises(AssetError, match="octet-stream"):
        _s3(_Transport()).put(str(odd), "thing.qqq")


# ---------------------------------------------------------------------- #
# Selection                                                               #
# ---------------------------------------------------------------------- #


def test_local_is_the_default(tmp_path, monkeypatch):
    for var in ("MOVIECREW_S3_BUCKET", "MOVIECREW_S3_ENDPOINT",
                "MOVIECREW_S3_ACCESS_KEY", "MOVIECREW_S3_SECRET_KEY"):
        monkeypatch.delenv(var, raising=False)
    store = build_asset_store(local_root=str(tmp_path))
    assert isinstance(store, LocalAssetStore)


def test_credentials_opt_into_the_bucket(tmp_path, monkeypatch):
    monkeypatch.setenv("MOVIECREW_S3_BUCKET", "films")
    monkeypatch.setenv("MOVIECREW_S3_ENDPOINT", "https://acct.r2.cloudflarestorage.com")
    monkeypatch.setenv("MOVIECREW_S3_ACCESS_KEY", "AK")
    monkeypatch.setenv("MOVIECREW_S3_SECRET_KEY", "SK")
    monkeypatch.setenv("MOVIECREW_ASSET_BASE_URL", "https://media.example.com")

    store = build_asset_store(local_root=str(tmp_path))
    assert isinstance(store, S3AssetStore)
    assert store.serves_public_urls is True


def test_partial_credentials_fall_back_rather_than_half_configuring(tmp_path, monkeypatch):
    monkeypatch.setenv("MOVIECREW_S3_BUCKET", "films")
    for var in ("MOVIECREW_S3_ENDPOINT", "MOVIECREW_S3_ACCESS_KEY", "MOVIECREW_S3_SECRET_KEY"):
        monkeypatch.delenv(var, raising=False)
    assert isinstance(build_asset_store(local_root=str(tmp_path)), LocalAssetStore)


def test_both_stores_satisfy_the_interface(tmp_path):
    assert isinstance(LocalAssetStore(str(tmp_path)), AssetStore)
    assert isinstance(_s3(_Transport()), AssetStore)


def test_asset_reports_its_own_reachability():
    assert Asset("k", "video/mp4", 1, "https://cdn.example.com/k").is_reachable is True
    assert Asset("k", "video/mp4", 1, "http://localhost/k").is_reachable is False
    assert Asset("k", "video/mp4", 1, None).is_reachable is False
