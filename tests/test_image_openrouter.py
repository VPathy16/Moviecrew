"""Tests for the OpenRouter-backed storyboard image provider.

Fully offline: the transport is injected, so no key and no network are
needed on any path.
"""

from __future__ import annotations

import base64

import pytest

from moviecrew.image import ImageProvider
from moviecrew.image_openrouter import (
    API_KEY_ENV,
    DEFAULT_MODEL,
    ImageError,
    OpenRouterImageProvider,
    decode_data_uri,
    image_uri_of,
)

_PNG = b"\x89PNG\r\n\x1a\n" + b"stub bytes"
_URI = "data:image/png;base64," + base64.b64encode(_PNG).decode()


class _Transport:
    def __init__(self, payloads):
        self._payloads = list(payloads)
        self.calls: list[dict] = []

    def __call__(self, method, url, headers, body):
        self.calls.append({"method": method, "url": url, "headers": headers, "body": body})
        payload = self._payloads.pop(0)
        if isinstance(payload, Exception):
            raise payload
        return payload


def _reply(images=None, content=None) -> dict:
    message: dict = {"role": "assistant"}
    if images is not None:
        message["images"] = images
    if content is not None:
        message["content"] = content
    return {"choices": [{"message": message}]}


def _provider(payloads, **kwargs) -> OpenRouterImageProvider:
    return OpenRouterImageProvider(transport=_Transport(payloads), **kwargs)


# ---------------------------------------------------------------------- #
# Data URI decoding                                                       #
# ---------------------------------------------------------------------- #


def test_data_uri_round_trips():
    assert decode_data_uri(_URI) == _PNG


def test_non_data_uri_is_rejected():
    with pytest.raises(ImageError, match="not a data URI"):
        decode_data_uri("https://example.com/a.png")


def test_non_base64_data_uri_is_rejected():
    with pytest.raises(ImageError, match="not base64"):
        decode_data_uri("data:image/png,rawbytes")


def test_corrupt_base64_fails_here_not_on_disk():
    """A bad payload must fail loudly rather than write a broken PNG."""
    with pytest.raises(ImageError, match="valid base64"):
        decode_data_uri("data:image/png;base64,!!!not-base64!!!")


# ---------------------------------------------------------------------- #
# Response shapes                                                         #
# ---------------------------------------------------------------------- #


def test_image_as_a_bare_string():
    assert image_uri_of(_reply(images=[_URI])) == _URI


def test_image_as_an_image_url_object():
    payload = _reply(images=[{"type": "image_url", "image_url": {"url": _URI}}])
    assert image_uri_of(payload) == _URI


def test_missing_image_surfaces_what_the_model_said():
    """A refusal or safety block explains itself in the text — show it."""
    payload = _reply(content="I can't generate that image.")
    with pytest.raises(ImageError, match="can't generate"):
        image_uri_of(payload)


def test_empty_choices_is_an_error_not_a_crash():
    with pytest.raises(ImageError, match="no choices"):
        image_uri_of({"choices": []})


# ---------------------------------------------------------------------- #
# The provider                                                            #
# ---------------------------------------------------------------------- #


def test_missing_key_raises_a_message_naming_the_variable(monkeypatch):
    monkeypatch.delenv(API_KEY_ENV, raising=False)
    with pytest.raises(ImageError, match=API_KEY_ENV):
        OpenRouterImageProvider()


def test_generate_returns_png_bytes():
    provider = _provider([_reply(images=[_URI])])
    assert provider.generate("a lighthouse at dusk", "sc1-sh1") == _PNG


def test_image_modality_is_requested():
    """Without this the model answers with prose and no image."""
    body = _provider([]).build_request("a lighthouse")
    assert body["modalities"] == ["image", "text"]
    assert body["model"] == DEFAULT_MODEL


def test_key_is_sent_as_a_bearer_header():
    transport = _Transport([_reply(images=[_URI])])
    OpenRouterImageProvider(api_key="sk-test", transport=transport).generate("p", "sc1-sh1")
    assert transport.calls[0]["headers"]["Authorization"] == "Bearer sk-test"


def test_error_payload_names_the_shot():
    """Mid-board, which shot failed matters as much as why."""
    provider = _provider([{"error": {"message": "content policy"}}])
    with pytest.raises(ImageError, match="sc2-sh7"):
        provider.generate("p", "sc2-sh7")


def test_it_is_an_image_provider():
    assert isinstance(_provider([]), ImageProvider)


def test_it_promotes_references():
    """A real generator's approved frame is worth anchoring later renders to;
    this flag is what StudioSession.approve() gates promotion on."""
    assert _provider([]).promotes_references is True


def test_a_board_of_stills_can_be_generated():
    """The storyboard gate calls generate() once per shot."""
    provider = _provider([_reply(images=[_URI]) for _ in range(3)])
    shots = ["sc1-sh1", "sc1-sh2", "sc1-sh3"]
    assert [provider.generate("p", shot) for shot in shots] == [_PNG] * 3
