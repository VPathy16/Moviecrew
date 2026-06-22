"""Tests for the VideoBackend abstraction, fully offline.

Builds a Project via MovieCrew + MockLLMClient, then runs StubVideoBackend
over it through MovieCrew.render() and checks the result list against the
render plan: one result per prompt, render_plan.order preserved, and request
payloads carrying the shot's reference images and clamped duration.
"""

from moviecrew.crew import MovieCrew
from moviecrew.mock import MockLLMClient
from moviecrew.schema import VEO_LEGAL_DURATIONS_S
from moviecrew.video import StubVideoBackend


def test_stub_backend_renders_every_prompt_in_order():
    project = MovieCrew(MockLLMClient()).make("A keeper and a sea spirit outlast a storm.")
    render_plan = project.render_plan
    assert render_plan is not None

    crew = MovieCrew(MockLLMClient())
    results = crew.render(project, StubVideoBackend())

    assert [result.shot_id for result in results] == render_plan.order
    assert len(results) == len(render_plan.prompts)

    prompts_by_shot_id = {prompt.shot_id: prompt for prompt in render_plan.prompts}
    for result in results:
        assert result.status == "stubbed"
        assert result.backend == "stub"
        assert result.uri is None

        prompt = prompts_by_shot_id[result.shot_id]
        assert result.raw["prompt"] == prompt.prompt
        assert result.raw["negative_prompt"] == prompt.negative_prompt
        assert result.raw["duration_s"] == prompt.duration_s
        assert result.raw["duration_s"] in VEO_LEGAL_DURATIONS_S
        assert result.raw["aspect_ratio"] == prompt.aspect_ratio
        assert result.raw["reference_images"] == prompt.reference_images


def test_chained_shots_pass_extend_from_to_the_backend():
    project = MovieCrew(MockLLMClient()).make("A keeper and a sea spirit outlast a storm.")
    render_plan = project.render_plan
    assert render_plan is not None
    assert render_plan.chains  # mock groups the two demo shots into one chain

    crew = MovieCrew(MockLLMClient())
    results = crew.render(project, StubVideoBackend())
    raw_by_shot_id = {result.shot_id: result.raw for result in results}

    predecessor_by_shot_id: dict[str, str] = {}
    for chain in render_plan.chains:
        for predecessor, shot_id in zip(chain, chain[1:]):
            predecessor_by_shot_id[shot_id] = predecessor

    for result in results:
        expected_extend_from = predecessor_by_shot_id.get(result.shot_id)
        assert raw_by_shot_id[result.shot_id]["extend_from"] == expected_extend_from
