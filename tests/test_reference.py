"""Tests for moviecrew.reference, fully offline."""

from __future__ import annotations

import os

from moviecrew.reference import (
    FileReferenceImageProvider,
    NullReferenceImageProvider,
    populate_reference_stills,
)
from moviecrew.schema import Bible, Character


def _character(char_id: str) -> Character:
    return Character(id=char_id, name=char_id, description="x")


def test_null_provider_returns_none():
    provider = NullReferenceImageProvider()
    assert provider.generate(_character("ch1")) is None


def test_file_provider_returns_bytes_for_existing_file(tmp_path):
    (tmp_path / "ch1.png").write_bytes(b"fake-png-bytes")
    provider = FileReferenceImageProvider(str(tmp_path))

    assert provider.generate(_character("ch1")) == b"fake-png-bytes"


def test_file_provider_returns_none_when_missing(tmp_path):
    provider = FileReferenceImageProvider(str(tmp_path))

    assert provider.generate(_character("ch1")) is None


class _FakeProvider:
    def __init__(self, bytes_by_id: dict[str, bytes]) -> None:
        self.bytes_by_id = bytes_by_id

    def generate(self, character):
        return self.bytes_by_id.get(character.id)


def test_populate_reference_stills_writes_only_produced_characters(tmp_path):
    bible = Bible(
        style="s",
        palette="p",
        mood="m",
        characters=[_character("ch1"), _character("ch2")],
    )
    out_dir = str(tmp_path / "stills")
    provider = _FakeProvider({"ch1": b"fake-png-bytes"})

    populated = populate_reference_stills(bible, provider, out_dir=out_dir)

    assert populated == ["ch1"]
    ch1, ch2 = bible.characters
    assert ch1.reference_images == [os.path.join(out_dir, "ch1.png")]
    assert os.path.isfile(ch1.reference_images[0])
    assert ch2.reference_images == []


def test_populate_reference_stills_is_a_no_op_with_null_provider(tmp_path):
    bible = Bible(style="s", palette="p", mood="m", characters=[_character("ch1")])
    out_dir = str(tmp_path / "stills")

    populated = populate_reference_stills(bible, NullReferenceImageProvider(), out_dir=out_dir)

    assert populated == []
    assert bible.characters[0].reference_images == []
    assert not os.path.isdir(out_dir)
