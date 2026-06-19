"""End-to-end test for the MovieCrew orchestrator, fully offline.

Runs the whole pipeline against MockLLMClient and checks the resulting
Project against the schema's hard constraints: legal shot durations, full
prompt coverage, a complete render order, and the deterministic continuity
check (scene has characters but a shot ended up with no reference images).
"""

import copy

from moviecrew.crew import MovieCrew
from moviecrew.mock import MockLLMClient, _RESPONSES
from moviecrew.schema import VEO_LEGAL_DURATIONS_S


def test_make_returns_a_consistent_project():
    project = MovieCrew(MockLLMClient()).make("A keeper and a sea spirit outlast a storm.")

    assert project.title
    assert project.logline
    assert project.outline

    assert len(project.scenes) >= 1
    for scene in project.scenes:
        assert len(scene.shots) >= 1
        for shot in scene.shots:
            assert shot.duration_s in VEO_LEGAL_DURATIONS_S

    all_shot_ids = {shot.id for scene in project.scenes for shot in scene.shots}

    render_plan = project.render_plan
    assert render_plan is not None

    prompt_shot_ids = {prompt.shot_id for prompt in render_plan.prompts}
    assert prompt_shot_ids == all_shot_ids

    assert set(render_plan.order) == all_shot_ids
    assert render_plan.est_duration_s == sum(
        shot.duration_s for scene in project.scenes for shot in scene.shots
    )


class _NoReferenceImagesLLMClient(MockLLMClient):
    """Same canned responses as MockLLMClient, but the Bible's characters
    and locations carry no reference images — forces the deterministic
    "scene has characters but shot has no reference images" check to fire.
    """

    def complete_json(self, *, task, system, user):
        result = copy.deepcopy(_RESPONSES[task])
        if task == "designer":
            for character in result["characters"]:
                character["reference_images"] = []
            for location in result["locations"]:
                location["reference_images"] = []
        return result


def test_deterministic_continuity_flag_fires_when_references_are_missing():
    project = MovieCrew(_NoReferenceImagesLLMClient()).make(
        "A keeper and a sea spirit outlast a storm."
    )

    scenes_with_characters = [s for s in project.scenes if s.character_ids]
    assert scenes_with_characters
    for scene in scenes_with_characters:
        for shot in scene.shots:
            assert shot.reference_image_ids == []

    missing_ref_flags = [
        f
        for f in project.render_plan.flags
        if f.kind == "warning" and "no reference images" in f.message
    ]
    assert missing_ref_flags
    flagged_shot_ids = {f.target for f in missing_ref_flags}
    expected_shot_ids = {
        shot.id for scene in scenes_with_characters for shot in scene.shots
    }
    assert flagged_shot_ids == expected_shot_ids
