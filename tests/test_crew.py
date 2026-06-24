"""End-to-end test for the MovieCrew orchestrator, fully offline.

Runs the whole pipeline against MockLLMClient and checks the resulting
Project against the schema's hard constraints: legal shot durations, full
prompt coverage, and a complete render order. With the default null
reference provider, nothing has a real reference still, so no shot anchors
(see tests/test_anchors.py for anchoring behavior).
"""

from moviecrew.crew import MovieCrew
from moviecrew.mock import MockLLMClient
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


def test_default_null_provider_anchors_nothing():
    project = MovieCrew(MockLLMClient()).make("A keeper and a sea spirit outlast a storm.")

    for scene in project.scenes:
        for shot in scene.shots:
            assert shot.consistency_anchor is False
            assert shot.reference_image_ids == []

    assert not any(
        f.kind == "warning" and "consistency anchor" in f.message
        for f in project.render_plan.flags
    )
