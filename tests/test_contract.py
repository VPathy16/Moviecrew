"""Contract test: every mock response must unpack directly into its dataclass.

For each task, the canned dict from MockLLMClient is passed straight into
the matching moviecrew.schema dataclass(es) via `**d` — no field renaming or
adaptation. If schema.py and mock.py ever drift (a renamed/removed field on
either side), the `**d` unpacking raises TypeError and this test fails.
"""

import pytest

from moviecrew.mock import MockLLMClient
from moviecrew.schema import (
    Bible,
    Character,
    ContinuityFlag,
    Location,
    Project,
    RenderPlan,
    Scene,
    Shot,
    VeoPrompt,
)


@pytest.fixture
def client() -> MockLLMClient:
    return MockLLMClient()


def test_director_contract(client: MockLLMClient):
    director = client.complete_json(task="director", system="", user="")
    assert director["title"]
    assert director["logline"]
    assert director["outline"]


def test_writer_contract(client: MockLLMClient):
    writer = client.complete_json(task="writer", system="", user="")
    for raw_scene in writer["scenes"]:
        scene = Scene(**raw_scene)
        assert scene.id
        assert scene.slug
        assert scene.title
        assert scene.summary


def test_designer_contract(client: MockLLMClient):
    designer = client.complete_json(task="designer", system="", user="")
    characters = [Character(**c) for c in designer["characters"]]
    locations = [Location(**l) for l in designer["locations"]]
    bible = Bible(
        style=designer["style"],
        palette=designer["palette"],
        mood=designer["mood"],
        characters=characters,
        locations=locations,
    )
    assert bible.style
    assert bible.palette
    assert bible.mood
    for character in characters:
        assert character.name
        assert character.description
        assert character.reference_images
    for location in locations:
        assert location.name
        assert location.description
        assert location.reference_images


def test_cinematographer_contract(client: MockLLMClient):
    cinematographer = client.complete_json(task="cinematographer", system="", user="")
    shots = [Shot(**s) for s in cinematographer["shots"]]
    assert shots
    for shot in shots:
        assert shot.description
        assert shot.duration_s
        assert shot.camera_move
        assert shot.lens
        assert shot.framing


def test_prompter_contract(client: MockLLMClient):
    prompter = client.complete_json(task="prompter", system="", user="")
    prompts = [VeoPrompt(**p) for p in prompter["prompts"]]
    assert prompts
    for prompt in prompts:
        assert prompt.prompt
        assert prompt.negative_prompt
        assert prompt.reference_images


def test_continuity_contract(client: MockLLMClient):
    continuity = client.complete_json(task="continuity", system="", user="")
    flags = [ContinuityFlag(**f) for f in continuity["flags"]]
    assert flags
    for flag in flags:
        assert flag.target
        assert flag.kind
        assert flag.message


def test_editor_contract(client: MockLLMClient):
    editor = client.complete_json(task="editor", system="", user="")
    render_plan = RenderPlan(**editor)
    assert render_plan.order
    assert render_plan.est_duration_s


def test_full_project_assembles_strictly_from_mock_responses(client: MockLLMClient):
    director = client.complete_json(task="director", system="", user="")
    writer = client.complete_json(task="writer", system="", user="")
    designer = client.complete_json(task="designer", system="", user="")
    cinematographer = client.complete_json(task="cinematographer", system="", user="")
    prompter = client.complete_json(task="prompter", system="", user="")
    continuity = client.complete_json(task="continuity", system="", user="")
    editor = client.complete_json(task="editor", system="", user="")

    bible = Bible(
        style=designer["style"],
        palette=designer["palette"],
        mood=designer["mood"],
        characters=[Character(**c) for c in designer["characters"]],
        locations=[Location(**l) for l in designer["locations"]],
    )

    shots_by_scene: dict[str, list[Shot]] = {}
    for raw_shot in cinematographer["shots"]:
        shot = Shot(**raw_shot)
        shots_by_scene.setdefault(shot.scene_id, []).append(shot)

    scenes = [
        Scene(**{**raw_scene, "shots": shots_by_scene.get(raw_scene["id"], [])})
        for raw_scene in writer["scenes"]
    ]

    prompts = [VeoPrompt(**p) for p in prompter["prompts"]]
    flags = [ContinuityFlag(**f) for f in continuity["flags"]]
    render_plan = RenderPlan(prompts=prompts, flags=flags, **editor)

    project = Project(
        title=director["title"],
        logline=director["logline"],
        outline=director["outline"],
        bible=bible,
        scenes=scenes,
        render_plan=render_plan,
    )

    assert project.title
    assert project.logline
    assert project.outline
    for scene in project.scenes:
        assert scene.summary
        for shot in scene.shots:
            assert shot.camera_move
    for character in project.bible.characters:
        assert character.reference_images
