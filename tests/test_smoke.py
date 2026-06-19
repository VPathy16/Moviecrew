"""End-to-end smoke test: MockLLMClient -> schema, fully offline.

Runs every task once, feeds the canned JSON into the dataclasses from
moviecrew.schema, and checks the result is internally consistent (ids
line up, every shot/prompt duration is a legal Veo clip length). No
network access and no API key required.
"""

from moviecrew.mock import MockLLMClient
from moviecrew.schema import (
    VEO_LEGAL_DURATIONS_S,
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

TASKS = [
    "director",
    "writer",
    "designer",
    "cinematographer",
    "prompter",
    "continuity",
    "editor",
]


def test_mock_client_answers_every_task():
    client = MockLLMClient()
    for task in TASKS:
        result = client.complete_json(task=task, system="", user="")
        assert isinstance(result, dict)
        assert result


def test_full_pipeline_builds_a_consistent_project():
    client = MockLLMClient()

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
        assert shot.duration_s in VEO_LEGAL_DURATIONS_S
        shots_by_scene.setdefault(shot.scene_id, []).append(shot)

    scenes = []
    for raw_scene in writer["scenes"]:
        scene = Scene(
            id=raw_scene["id"],
            slug=raw_scene["slug"],
            title=raw_scene["title"],
            summary=raw_scene["summary"],
            location_id=raw_scene["location_id"],
            character_ids=raw_scene["character_ids"],
            shots=shots_by_scene.get(raw_scene["id"], []),
        )
        scenes.append(scene)

    prompts = [VeoPrompt(**p) for p in prompter["prompts"]]
    for prompt in prompts:
        assert prompt.duration_s in VEO_LEGAL_DURATIONS_S

    flags = [ContinuityFlag(**f) for f in continuity["flags"]]

    render_plan = RenderPlan(
        prompts=prompts,
        flags=flags,
        order=editor["order"],
        est_duration_s=editor["est_duration_s"],
    )

    project = Project(
        title=director["title"],
        logline=director["logline"],
        outline=director["outline"],
        bible=bible,
        scenes=scenes,
        render_plan=render_plan,
    )

    # All shot ids referenced by prompts/flags/order must exist in the scenes.
    all_shot_ids = {shot.id for scene in project.scenes for shot in scene.shots}
    for prompt in project.render_plan.prompts:
        assert prompt.shot_id in all_shot_ids
    for flag in project.render_plan.flags:
        assert flag.target in all_shot_ids
    for shot_id in project.render_plan.order:
        assert shot_id in all_shot_ids

    # Every shot duration is a legal Veo clip length.
    for scene in project.scenes:
        for shot in scene.shots:
            assert shot.duration_s in VEO_LEGAL_DURATIONS_S

    # The whole thing must serialize cleanly.
    data = project.to_dict()
    assert data["title"] == director["title"]
    assert project.to_json()
