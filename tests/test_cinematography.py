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


def test_registry_has_no_dangling_conflicts_with_or_pairs_with_references():
    # requires deliberately may reference non-technique preconditions (see
    # Technique's docstring) - conflicts_with/pairs_with must not; the module
    # self-checks this at import time, this test re-asserts it explicitly
    # so a future regression fails a test, not just a fresh interpreter start.
    for technique in TECHNIQUES.values():
        for attr in ("conflicts_with", "pairs_with"):
            for ref in getattr(technique, attr):
                assert ref in TECHNIQUES, f"{technique.id}.{attr} references unknown id {ref!r}"


def test_registry_has_no_duplicate_ids_and_every_supports_intent_is_valid():
    ids = [t.id for t in TECHNIQUES.values()]
    assert len(ids) == len(set(ids))
    for technique in TECHNIQUES.values():
        assert set(technique.supports_intent) <= set(NARRATIVE_INTENTS)


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


def test_cinematic_spec_from_dict_tolerates_extra_llm_metadata_without_crashing():
    # The exact failure mode crew._shot_from_raw's own docstring names as
    # routine LLM behavior ("note", "rationale", "transition" have all shown
    # up unasked-for in practice) - CameraSpec(**raw) would crash on it.
    spec = CinematicSpec.from_dict({
        "camera": {"shot_scale_start": "cu", "note": "dramatic reveal", "confidence": 0.9},
        "focus": {"mode": "rack", "reasoning": "draws the eye"},
    })
    assert spec.camera.shot_scale_start == "cu"
    assert spec.focus.mode == "rack"


def test_cinematic_spec_from_dict_tolerates_wrong_types_without_crashing():
    spec = CinematicSpec.from_dict({"camera": "wide shot", "technique_ids": "not_a_list", "rationale": None})
    assert spec.camera == CameraSpec()
    assert spec.technique_ids == []
    assert spec.rationale == ""


def test_cinematic_spec_from_dict_coerces_lens_mm_to_int():
    assert CinematicSpec.from_dict({"camera": {"lens_mm": 65.0}}).camera.lens_mm == 65
    assert CinematicSpec.from_dict({"camera": {"lens_mm": "not-a-number"}}).camera.lens_mm is None


def test_cinematic_spec_from_dict_coerces_nested_list_fields_not_just_top_level():
    # Same risk as technique_ids/narrative_intents, one level deeper: a
    # string where composition.techniques/acceptance.* expect a list would
    # otherwise iterate character-by-character downstream instead of
    # erroring or emptying cleanly.
    spec = CinematicSpec.from_dict({
        "composition": {"techniques": "wide"},
        "acceptance": {"must": "identity", "prefer": ["65mm_feel"], "avoid": 42},
    })
    assert spec.composition.techniques == []
    assert spec.acceptance.must == []
    assert spec.acceptance.prefer == ["65mm_feel"]
    assert spec.acceptance.avoid == []

    good = CinematicSpec.from_dict({
        "composition": {"techniques": ["thirds", "negative_space"]},
        "acceptance": {"must": ["identity", "reveal"]},
    })
    assert good.composition.techniques == ["thirds", "negative_space"]
    assert good.acceptance.must == ["identity", "reveal"]


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
                     cut_reason="Confirm the dread in a separate frame",
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


def test_cinematic_spec_and_beats_survive_pipeline_and_reload(tmp_path, monkeypatch):
    """The duration-budget and cinematic-spec features must coexist on one shot."""
    from moviecrew import projects
    from moviecrew.agents import CinematographerAgent
    from moviecrew.image import MockImageProvider
    from moviecrew.schema import Beat
    from moviecrew.studio import StudioSession, Stage

    class CombinedLLM(_CILLLM):
        def complete_json(self, *, task, system, user):
            result = super().complete_json(task=task, system=system, user=user)
            if task == 'writer':
                result['scenes'][0]['target_duration_s'] = 7
            if task == 'cinematographer':
                result['shots'][0]['beats'] = [
                    {'start_s': 0, 'end_s': 2, 'action': 'Read the message'},
                    {'start_s': 2, 'end_s': 4, 'action': 'Look up in recognition'},
                ]
                result['shots'][1]['cut_reason'] = 'Reveal the reaction'
            return result

    llm = CombinedLLM()
    project = MovieCrew(llm).make('A concept', run_continuity=False)
    shot = project.scenes[0].shots[0]
    assert isinstance(shot.beats[0], Beat)
    assert shot.cinematic_spec.camera.movement_type == 'push_in'
    context = project.render_plan.intents[0].direction_context
    assert context['current_shot']['beats'][1]['end_s'] == 4
    assert 'push-in' in context['cinematic_direction'].lower()
    assert llm.cine_user['scene']['target_duration_s'] == 7

    monkeypatch.setenv('MOVIECREW_PROJECTS_ROOT', str(tmp_path / 'db'))
    session = StudioSession('combined', Stage.SHOT_DEFS, project,
                            str(tmp_path / 'media'), MockImageProvider())
    projects.save(session)
    restored = projects.load('combined', MockImageProvider()).project
    assert restored == project
    assert isinstance(restored.scenes[0].shots[0].beats[0], Beat)
    assert isinstance(restored.scenes[0].shots[0].cinematic_spec, CinematicSpec)


def test_shot_from_raw_reconstructs_beats_and_cinematic_spec():
    from moviecrew.crew import _shot_from_raw
    from moviecrew.schema import Beat, CinematicSpec

    raw = {
        "id": "sc1-sh1",
        "scene_id": "sc1",
        "description": "Opening shot",
        "duration_s": 6.0,
        "story_contract_version": 1,
        "purpose": "establish mood",
        "action": "walking down alley",
        "entry_state": {"loc": "street"},
        "exit_state": {"loc": "doorway"},
        "cut_reason": "reveal interior",
        "beats": [
            {"start_s": 0.0, "end_s": 3.0, "action": "walk forward"},
            {"start_s": 3.0, "end_s": 6.0, "action": "pause at door"},
        ],
        "cinematic_spec": {
            "camera": {"movement_type": "tracking", "lens_mm": 35},
            "technique_ids": ["tracking"],
            "rationale": "follow character pace",
        },
        "extraneous_key": "should be ignored",
    }
    shot = _shot_from_raw(raw)
    assert shot.id == "sc1-sh1"
    assert len(shot.beats) == 2
    assert all(isinstance(b, Beat) for b in shot.beats)
    assert shot.beats[0].action == "walk forward"
    assert shot.cut_reason == "reveal interior"
    assert isinstance(shot.cinematic_spec, CinematicSpec)
    assert shot.cinematic_spec.camera.movement_type == "tracking"
    assert shot.cinematic_spec.camera.lens_mm == 35
    assert not hasattr(shot, "extraneous_key")


def test_projects_load_backward_compatible_without_spec_or_beats(tmp_path, monkeypatch):
    from moviecrew import projects
    from moviecrew.image import MockImageProvider
    from moviecrew.schema import Project, Scene, Shot, Bible
    from moviecrew.studio import StudioSession, Stage

    monkeypatch.setenv("MOVIECREW_PROJECTS_ROOT", str(tmp_path / "db"))
    old_project = Project(
        title="Old Film",
        logline="Logline",
        bible=Bible(style="noir", palette="monochrome", mood="tense"),
        scenes=[
            Scene(
                id="sc1",
                slug="s1",
                title="Scene 1",
                summary="summary",
                shots=[
                    Shot(
                        id="sc1-sh1",
                        scene_id="sc1",
                        description="shot 1",
                        duration_s=4.0,
                    )
                ],
            )
        ],
    )
    session = StudioSession("legacy-project", Stage.SHOT_DEFS, old_project,
                            str(tmp_path / "media"), MockImageProvider())
    projects.save(session)
    restored = projects.load("legacy-project", MockImageProvider()).project
    loaded_shot = restored.scenes[0].shots[0]
    assert loaded_shot.cinematic_spec is None
    assert loaded_shot.beats == []


def test_duration_budget_replanning_with_cinematic_spec():
    """Replanning triggered by over-budget duration works when cinematic_spec is present."""
    class OverBudgetWithCineLLM(MockLLMClient):
        def __init__(self):
            self.cine_calls = 0

        def complete_json(self, *, task, system, user):
            if task == "writer":
                return {"scenes": [dict(id="sc1", slug="s1", title="Scene 1", summary="s",
                                         location_id="loc1", character_ids=["ch1"],
                                         target_duration_s=10.0)]}
            if task == "cinematographer":
                self.cine_calls += 1
                if self.cine_calls == 1:
                    # Over-budget: 3 shots totaling 20s (> 10 * 1.5 = 15s)
                    return {"shots": [
                        dict(id="sc1-sh1", scene_id="sc1", description="a", duration_s=8,
                             story_contract_version=1, purpose="p1", action="a1",
                             entry_state={"x": "1"}, exit_state={"x": "2"}, transition="cut",
                             cinematic_spec={"camera": {"movement_type": "push_in"}, "technique_ids": ["push_in"]}),
                        dict(id="sc1-sh2", scene_id="sc1", description="b", duration_s=7,
                             story_contract_version=1, purpose="p2", action="a2", cut_reason="cut to reaction",
                             entry_state={"x": "2"}, exit_state={"x": "3"}, transition="cut",
                             cinematic_spec={"camera": {"movement_type": "static"}, "technique_ids": ["static"]}),
                        dict(id="sc1-sh3", scene_id="sc1", description="c", duration_s=5,
                             story_contract_version=1, purpose="p3", action="a3", cut_reason="cut to reveal",
                             entry_state={"x": "3"}, exit_state={"x": "4"}, transition="cut",
                             cinematic_spec={"camera": {"movement_type": "static"}, "technique_ids": ["static"]}),
                    ]}
                else:
                    # Replanned: 1 shot with 2 beats totaling 9s (under budget)
                    return {"shots": [
                        dict(id="sc1-sh1", scene_id="sc1", description="combined", duration_s=9,
                             story_contract_version=1, purpose="p1", action="combined action",
                             entry_state={"x": "1"}, exit_state={"x": "4"}, transition="cut",
                             beats=[
                                 {"start_s": 0.0, "end_s": 4.5, "action": "part 1"},
                                 {"start_s": 4.5, "end_s": 9.0, "action": "part 2"},
                             ],
                             cinematic_spec={"camera": {"movement_type": "push_in"}, "technique_ids": ["push_in"]}),
                    ]}
            if task == "prompter":
                data = json.loads(user)
                return {"prompts": [{"shot_id": data["shot"]["id"],
                                      "prompt": f"Prompt for {data['shot']['id']}.",
                                      "negative_prompt": ""}]}
            return super().complete_json(task=task, system=system, user=user)

    llm = OverBudgetWithCineLLM()
    project = MovieCrew(llm).make("A concept", target_duration_s=10.0, run_continuity=False)
    assert llm.cine_calls == 2  # Replanning was triggered
    assert len(project.scenes[0].shots) == 1
    shot = project.scenes[0].shots[0]
    assert shot.duration_s == 9
    assert len(shot.beats) == 2
    assert shot.cinematic_spec.camera.movement_type == "push_in"
    assert not any("used" in f.message and "target" in f.message for f in project.render_plan.flags)

