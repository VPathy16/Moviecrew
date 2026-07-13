"""Tests for assets-first mode: Bible-as-input, library save/load, merge rules.

Fully offline — uses MockLLMClient, no network, no API keys.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from moviecrew.crew import MovieCrew
from moviecrew.library import load_bible, save_bible
from moviecrew.mock import MockLLMClient
from moviecrew.reference import NullReferenceImageProvider, populate_reference_stills
from moviecrew.schema import Bible, Character, Location, Prop


# ---------------------------------------------------------------------- #
# Schema: Prop + Bible.to_dict / Bible.from_dict                         #
# ---------------------------------------------------------------------- #


def test_prop_dataclass_defaults():
    p = Prop(id="p1", name="Lantern", description="brass")
    assert p.reference_images == []


def test_bible_round_trips_through_to_dict_from_dict():
    bible = Bible(
        style="watercolor",
        palette="blue, grey",
        mood="tense",
        characters=[Character(id="ch1", name="Mara", description="keeper")],
        locations=[Location(id="loc1", name="Cliff", description="black rock")],
        props=[Prop(id="prop1", name="Lantern", description="brass")],
    )
    d = bible.to_dict()
    restored = Bible.from_dict(d)

    assert restored.style == bible.style
    assert restored.palette == bible.palette
    assert restored.mood == bible.mood
    assert len(restored.characters) == 1
    assert restored.characters[0].id == "ch1"
    assert len(restored.locations) == 1
    assert restored.locations[0].id == "loc1"
    assert len(restored.props) == 1
    assert restored.props[0].name == "Lantern"


def test_from_dict_tolerates_missing_props_key():
    data = {
        "style": "s",
        "palette": "p",
        "mood": "m",
        "characters": [],
        "locations": [],
    }
    bible = Bible.from_dict(data)
    assert bible.props == []


# ---------------------------------------------------------------------- #
# Library: save_bible / load_bible                                        #
# ---------------------------------------------------------------------- #


def test_save_bible_creates_bible_json_and_stills_dir(tmp_path):
    bible = Bible(
        style="muted watercolor",
        palette="slate blue",
        mood="tense",
        props=[Prop(id="prop1", name="Lantern", description="brass")],
    )
    out = save_bible(bible, tmp_path)
    assert out == tmp_path / "bible.json"
    assert out.exists()
    assert (tmp_path / "stills").is_dir()

    saved = json.loads(out.read_text())
    assert saved["style"] == "muted watercolor"
    assert saved["props"][0]["id"] == "prop1"


def test_load_bible_round_trips_all_fields(tmp_path):
    original = Bible(
        style="dark realism",
        palette="charcoal, crimson",
        mood="ominous",
        characters=[
            Character(id="ch1", name="Victor", description="villain", reference_images=[])
        ],
        locations=[
            Location(id="loc1", name="Manor", description="crumbling estate")
        ],
        props=[Prop(id="prop1", name="Dagger", description="ivory handle")],
    )
    save_bible(original, tmp_path)
    loaded = load_bible(tmp_path)

    assert loaded.style == original.style
    assert loaded.palette == original.palette
    assert loaded.mood == original.mood
    assert loaded.characters[0].id == "ch1"
    assert loaded.locations[0].id == "loc1"
    assert loaded.props[0].id == "prop1"


def test_load_bible_resolves_relative_ref_against_stills_dir(tmp_path):
    stills = tmp_path / "stills"
    stills.mkdir()
    still_file = stills / "ch1.png"
    still_file.write_bytes(b"PNG")

    data = {
        "style": "s",
        "palette": "p",
        "mood": "m",
        "characters": [
            {"id": "ch1", "name": "Mara", "description": "keeper",
             "reference_images": ["ch1.png"]}
        ],
        "locations": [],
        "props": [],
    }
    (tmp_path / "bible.json").write_text(json.dumps(data))

    loaded = load_bible(tmp_path)
    resolved = loaded.characters[0].reference_images[0]
    assert Path(resolved) == stills / "ch1.png"
    assert Path(resolved).exists()


def test_load_bible_keeps_missing_files_in_refs(tmp_path):
    """Paths that don't exist must be preserved, not silently dropped."""
    data = {
        "style": "s",
        "palette": "p",
        "mood": "m",
        "characters": [
            {"id": "ch1", "name": "X", "description": "d",
             "reference_images": ["nonexistent.png"]}
        ],
        "locations": [],
        "props": [],
    }
    (tmp_path / "bible.json").write_text(json.dumps(data))
    (tmp_path / "stills").mkdir()

    loaded = load_bible(tmp_path)
    assert loaded.characters[0].reference_images  # path kept even though missing
    assert "nonexistent.png" in loaded.characters[0].reference_images[0]


def test_load_bible_keeps_absolute_paths_unchanged(tmp_path):
    existing = tmp_path / "somewhere" / "ch1.png"
    existing.parent.mkdir()
    existing.write_bytes(b"PNG")

    data = {
        "style": "s",
        "palette": "p",
        "mood": "m",
        "characters": [
            {"id": "ch1", "name": "X", "description": "d",
             "reference_images": [str(existing)]}
        ],
        "locations": [],
        "props": [],
    }
    (tmp_path / "bible.json").write_text(json.dumps(data))
    (tmp_path / "stills").mkdir()

    loaded = load_bible(tmp_path)
    assert loaded.characters[0].reference_images[0] == str(existing)


# ---------------------------------------------------------------------- #
# crew.py: make(concept, bible=...) — assets-first mode                  #
# ---------------------------------------------------------------------- #


@pytest.fixture()
def provided_bible() -> Bible:
    return Bible(
        style="hand-drawn sketch",
        palette="sepia, ash",
        mood="wistful",
        characters=[
            Character(
                id="ch1",
                name="PROVIDED_MARA",
                description="PROVIDED description — must survive merge",
                reference_images=[],
            )
        ],
        locations=[
            Location(id="loc1", name="PROVIDED_Cliff", description="PROVIDED cliff")
        ],
        props=[Prop(id="prop1", name="PROVIDED_Lantern", description="PROVIDED lantern")],
    )


def test_make_with_bible_preserves_provided_characters(provided_bible):
    crew = MovieCrew(MockLLMClient())
    project = crew.make("A lighthouse story", bible=provided_bible)

    ch1 = next((c for c in project.bible.characters if c.id == "ch1"), None)
    assert ch1 is not None, "ch1 must survive the merge"
    assert ch1.name == "PROVIDED_MARA"
    assert "PROVIDED description" in ch1.description


def test_make_with_bible_preserves_provided_locations(provided_bible):
    crew = MovieCrew(MockLLMClient())
    project = crew.make("A story", bible=provided_bible)

    loc1 = next((l for l in project.bible.locations if l.id == "loc1"), None)
    assert loc1 is not None
    assert loc1.name == "PROVIDED_Cliff"


def test_make_with_bible_preserves_provided_props(provided_bible):
    crew = MovieCrew(MockLLMClient())
    project = crew.make("A story", bible=provided_bible)

    prop1 = next((p for p in project.bible.props if p.id == "prop1"), None)
    assert prop1 is not None
    assert prop1.name == "PROVIDED_Lantern"


def test_make_without_bible_works_unchanged():
    crew = MovieCrew(MockLLMClient())
    project = crew.make("A lighthouse story")
    assert project.title
    assert project.render_plan.prompts
    assert project.bible.props  # mock now includes prop1


def test_make_with_bible_still_produces_render_plan(provided_bible):
    crew = MovieCrew(MockLLMClient())
    project = crew.make("A story", bible=provided_bible)
    assert project.render_plan is not None
    assert project.render_plan.prompts


# ---------------------------------------------------------------------- #
# populate_reference_stills: library stills win                           #
# ---------------------------------------------------------------------- #


def test_populate_reference_stills_skips_asset_with_existing_file(tmp_path):
    existing_still = tmp_path / "ch1.png"
    existing_still.write_bytes(b"REAL_STILL")

    ch = Character(id="ch1", name="Mara", description="d",
                   reference_images=[str(existing_still)])
    bible = Bible(style="s", palette="p", mood="m", characters=[ch])

    class NeverCall(NullReferenceImageProvider):
        def generate(self, character):
            raise AssertionError("provider must not be called for library assets")

    populate_reference_stills(bible, NeverCall(), out_dir=str(tmp_path / "out"))

    # reference_images must still point to the original library still
    assert bible.characters[0].reference_images == [str(existing_still)]


def test_populate_reference_stills_still_runs_for_assets_without_existing_stills(tmp_path):
    ch = Character(id="ch1", name="Mara", description="d", reference_images=[])
    bible = Bible(style="s", palette="p", mood="m",
                  characters=[ch],
                  locations=[Location(id="loc1", name="Cliff", description="d")])

    from moviecrew.reference import FileReferenceImageProvider

    stills_dir = tmp_path / "ref"
    stills_dir.mkdir()
    (stills_dir / "ch1.png").write_bytes(b"STILL_BYTES")

    out_dir = str(tmp_path / "out")
    populated = populate_reference_stills(
        bible, FileReferenceImageProvider(str(stills_dir)), out_dir=out_dir
    )
    assert "ch1" in populated
    assert bible.characters[0].reference_images


# ---------------------------------------------------------------------- #
# Anchor fires from a library character with a real still                 #
# ---------------------------------------------------------------------- #


def test_anchor_fires_for_library_character_with_real_still(tmp_path):
    # Create a real PNG still for ch1 in the library's stills dir.
    stills = tmp_path / "stills"
    stills.mkdir()
    still_file = stills / "ch1.png"
    still_file.write_bytes(b"STUB_PNG")

    library_bible = Bible(
        style="s",
        palette="p",
        mood="m",
        characters=[
            Character(
                id="ch1",
                name="Mara",
                description="keeper",
                reference_images=[str(still_file)],  # real file
            )
        ],
        locations=[Location(id="loc1", name="Cliff", description="cliff")],
    )

    crew = MovieCrew(MockLLMClient())
    project = crew.make("A lighthouse story", bible=library_bible)

    all_shots = [s for scene in project.scenes for s in scene.shots]
    assert any(s.consistency_anchor for s in all_shots), (
        "at least one shot should be a consistency anchor when a character "
        "has a library still"
    )


# ---------------------------------------------------------------------- #
# CLI --save-bible / --bible round-trip                                   #
# ---------------------------------------------------------------------- #


def test_cli_save_bible_then_load_reproduces_cast(tmp_path):
    from moviecrew.cli import main

    lib_dir = str(tmp_path / "lib")

    # Story-first run; save the bible.
    ret = main(["a lighthouse story", "--backend", "mock", "--save-bible", lib_dir])
    assert ret == 0
    assert (Path(lib_dir) / "bible.json").exists()

    # Load the library and verify the cast round-trips.
    loaded = load_bible(lib_dir)
    assert loaded.style
    assert loaded.characters
    assert loaded.characters[0].id == "ch1"
    assert loaded.props
    assert loaded.props[0].id == "prop1"


def test_cli_bible_flag_runs_assets_first(tmp_path):
    from moviecrew.cli import main

    lib_dir = str(tmp_path / "lib")
    # First save a bible.
    main(["concept", "--backend", "mock", "--save-bible", lib_dir])

    # Now run in assets-first mode; must succeed and produce a project.
    out_path = str(tmp_path / "project.json")
    ret = main(["concept", "--backend", "mock", "--bible", lib_dir, "--out", out_path])
    assert ret == 0
    assert Path(out_path).exists()
    project_data = json.loads(Path(out_path).read_text())
    assert project_data["title"]
    assert project_data["bible"]["characters"]
