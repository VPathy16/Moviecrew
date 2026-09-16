"""Coverage for the Cinematography Intelligence Layer (CIL) Phase 0/1:
the technique registry, the optional CinematicSpec beside Shot's existing
prose fields, and the Cinematographer -> compiler -> Prompter wiring.

Deliberately NOT sized like a 424-entry catalogue clone — see
moviecrew/cinematography.py's module docstring for why.
"""
import json

import pytest

from moviecrew.cinematography import (
    CATEGORIES,
    NARRATIVE_INTENTS,
    TECHNIQUES,
    Technique,
    check_conflicts,
    cinematic_spec_flags,
    compile_cinematic_spec_summary,
)
from moviecrew.crew import MovieCrew
from moviecrew.mock import MockLLMClient
from moviecrew.schema import CameraSpec, CinematicSpec, CompositionSpec, FocusSpec, LightingSpec, Shot


def test_registry_is_mvp_sized_not_a_catalogue_clone():
    # "~60", deliberately not anywhere near the 424-entry bible this isn't.
    assert 55 <= len(TECHNIQUES) <= 75
    for category in CATEGORIES:
        assert len([t for t in TECHNIQUES.values() if t.category == category]) >= 5


def test_technique_rejects_an_intent_outside_the_shared_vocabulary():
    with pytest.raises(ValueError, match="unknown intent"):
        Technique(id="x", category="movement", name="X", description="d",
                  supports_intent=("not_a_real_intent",))


def test_check_conflicts_is_symmetric_regardless_of_which_side_declares_it():
    # handheld declares conflicts_with=('static',); static does not declare the reverse.
    assert check_conflicts(["handheld", "static"]) == [("handheld", "static")]
    assert check_conflicts(["static", "handheld"]) == [("handheld", "static")]
    assert check_conflicts(["cut", "wide"]) == []


def test_cinematic_spec_round_trips_through_its_own_dict():
    spec = CinematicSpec(
        camera=CameraSpec(angle="low_angle", lens_mm=35),
        composition=CompositionSpec(techniques=["thirds"]),
        technique_ids=["low_angle", "thirds"],
        narrative_intents=["dominate"],
        rationale="villain enters",
    )
    assert CinematicSpec.from_dict(spec.to_dict()) == spec


def test_shot_cinematic_spec_defaults_to_none():
    shot = Shot(id="s0", scene_id="sc1", description="x", duration_s=3)
    assert shot.cinematic_spec is None
    assert cinematic_spec_flags(shot) == []


def test_cinematic_spec_flags_catches_unknown_and_conflicting_ids():
    clean = Shot(id="s1", scene_id="sc1", description="x", duration_s=3,
                 cinematic_spec=CinematicSpec(technique_ids=["low_angle", "wide"]))
    assert cinematic_spec_flags(clean) == []

    messy = Shot(id="s2", scene_id="sc1", description="x", duration_s=3,
                 cinematic_spec=CinematicSpec(technique_ids=["static", "handheld", "made_up_technique"]))
    flags = cinematic_spec_flags(messy)
    assert any("unknown technique id" in f.message for f in flags)
    assert any("conflicting techniques" in f.message for f in flags)
    assert all(f.target == "s2" and f.kind == "warning" for f in flags)


def test_compile_cinematic_spec_summary_resolves_ids_to_real_language():
    spec = CinematicSpec(
        camera=CameraSpec(movement_type="push_in", movement_speed="slow", lens_mm=65),
        focus=FocusSpec(mode="rack", rack_from="eyes", rack_to="phone"),
        lighting=LightingSpec(key="window_light"),
        narrative_intents=["reveal", "intimate"],
    )
    summary = compile_cinematic_spec_summary(spec)
    assert "push-in" in summary.lower()  # resolved from the id, not the raw id itself
    assert "push_in" not in summary
    assert "slow" in summary
    assert "65mm" in summary
    assert "rack focus eyes to phone" in summary
    assert "window-side light" in summary.lower()
    assert "Intent: reveal, intimate" in summary


def test_compile_cinematic_spec_summary_is_empty_for_a_spec_with_nothing_set():
    assert compile_cinematic_spec_summary(CinematicSpec()) == ""


class _CILLLM(MockLLMClient):
    """One scene, two shots: the first gets a real, structured
    cinematic_spec; the second gets a deliberately conflicting one, to
    exercise the lint path end to end."""

    def __init__(self):
        self.cine_user = None
        self.prompter_calls = []

    def complete_json(self, *, task, system, user):
        if task == "writer":
            return {"scenes": [dict(id="sc1", slug="s1", title="Scene 1", summary="s",
                                     location_id="loc1", character_ids=["ch1"])]}
        if task == "cinematographer":
            self.cine_user = json.loads(user)
            return {"shots": [
                dict(id="sc1-sh1", scene_id="sc1", description="a", duration_s=4,
                     story_contract_version=1, purpose="reveal the betrayer", action="eyes widen",
                     entry_state={"x": "calm"}, exit_state={"x": "shocked"}, transition="cut",
                     cinematic_spec={
                         "camera": {"movement_type": "push_in", "movement_speed": "slow",
                                    "shot_scale_start": "mcu", "shot_scale_end": "cu"},
                         "focus": {"mode": "rack", "rack_from": "eyes", "rack_to": "phone"},
                         "lighting": {"key": "window_light"},
                         "composition": {"techniques": ["negative_space"]},
                         "technique_ids": ["push_in", "rack_focus", "window_light", "negative_space"],
                         "narrative_intents": ["reveal", "intimate"],
                         "rationale": "the reveal lands as recognition, not exposition",
                     }),
                dict(id="sc1-sh2", scene_id="sc1", description="b", duration_s=3,
                     story_contract_version=1, purpose="confirm the dread", action="he looks away",
                     entry_state={"x": "shocked"}, exit_state={"x": "resolved"}, transition="cut",
                     cinematic_spec={"technique_ids": ["static", "handheld"]}),
            ]}
        if task == "prompter":
            data = json.loads(user)
            self.prompter_calls.append(data)
            return {"prompts": [{"shot_id": data["shot"]["id"],
                                  "prompt": f"Placeholder action for {data['shot']['id']}.",
                                  "negative_prompt": ""}]}
        return super().complete_json(task=task, system=system, user=user)


def test_cinematographer_catalogue_reaches_the_model():
    llm = _CILLLM()
    MovieCrew(llm).make("A concept", run_continuity=False)
    assert llm.cine_user is not None
    catalogue_ids = {t["id"] for t in llm.cine_user["technique_catalogue"]}
    assert {"push_in", "rack_focus", "window_light", "negative_space"} <= catalogue_ids
    # Grouped by category, as the system prompt tells the model to expect.
    categories_seen = {t["category"] for t in llm.cine_user["technique_catalogue"]}
    assert categories_seen == set(CATEGORIES)


def test_shot_cinematic_spec_survives_into_the_finished_project():
    llm = _CILLLM()
    project = MovieCrew(llm).make("A concept", run_continuity=False)
    shots = {s.id: s for scene in project.scenes for s in scene.shots}

    spec = shots["sc1-sh1"].cinematic_spec
    assert spec is not None
    assert spec.camera.movement_type == "push_in"
    assert spec.focus.rack_from == "eyes" and spec.focus.rack_to == "phone"
    assert spec.rationale == "the reveal lands as recognition, not exposition"


def test_prompter_context_carries_the_compiled_direction_not_just_the_raw_spec():
    llm = _CILLLM()
    project = MovieCrew(llm).make("A concept", run_continuity=False)
    intents_by_id = {i.shot_id: i for i in project.render_plan.intents}

    direction = intents_by_id["sc1-sh1"].direction_context.get("cinematic_direction")
    assert direction is not None
    assert "push-in" in direction.lower()
    assert "rack focus eyes to phone" in direction

    # The raw spec is still there too (via current_shot's own asdict), just
    # not what the Prompter is told to treat as the compiled direction.
    assert intents_by_id["sc1-sh1"].direction_context["current_shot"]["cinematic_spec"]["camera"]["movement_type"] == "push_in"


def test_conflicting_technique_ids_surface_as_a_render_plan_warning():
    llm = _CILLLM()
    project = MovieCrew(llm).make("A concept", run_continuity=False)
    warnings = [f for f in project.render_plan.flags if f.target == "sc1-sh2"]
    assert any("conflicting techniques" in f.message for f in warnings)


def test_default_mock_pipeline_never_adds_cinematic_direction_when_no_spec_given():
    project = MovieCrew(MockLLMClient()).make("A keeper and a sea spirit outlast a storm.")
    for intent in project.render_plan.intents:
        assert "cinematic_direction" not in intent.direction_context


def test_cinematic_spec_round_trips_through_project_save_and_load(tmp_path, monkeypatch):
    from moviecrew import projects
    from moviecrew.image import MockImageProvider
    from moviecrew.studio import StudioSession, Stage

    monkeypatch.setenv("MOVIECREW_PROJECTS_ROOT", str(tmp_path / "db"))
    session = StudioSession("cil-project", Stage.SHOT_DEFS,
                             MovieCrew(_CILLLM()).make("A concept", run_continuity=False),
                             str(tmp_path / "media"), MockImageProvider())
    projects.save(session)
    restored = projects.load("cil-project", MockImageProvider())

    shot = next(s for scene in restored.project.scenes for s in scene.shots if s.id == "sc1-sh1")
    assert isinstance(shot.cinematic_spec, CinematicSpec)
    assert shot.cinematic_spec.camera.movement_type == "push_in"
