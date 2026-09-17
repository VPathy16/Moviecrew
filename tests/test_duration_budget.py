"""Coverage for the scene duration-budget fix and the per-shot pacing policy.

Root cause being fixed: nothing previously compared a shot's requested
duration to what the narrative moment actually needed, so a plan-once
Cinematographer would routinely turn a 10-second beat into eight 5-second
shots. These tests cover: Beat/cut_reason schema validation, target_duration_s
propagation from a film-level request down to each Scene, the bounded
one-retry budget check, that every bit of this is a no-op (byte-identical
old behavior) when target_duration_s is never supplied, and the always-on
per-shot pacing floor/ceiling (MIN_SHOT_DURATION_S/MAX_SHOT_DURATION_S) that
shares the same bounded-retry-then-clamp mechanism.
"""
import json

import pytest

from moviecrew.crew import MAX_SHOT_DURATION_S, MIN_SHOT_DURATION_S, MovieCrew, PipelineError
from moviecrew.mock import MockLLMClient
from moviecrew.schema import Beat, Shot


def _shot(shot_id, index=0, **overrides):
    """A causally-chained shot: exit_state[index] == entry_state[index+1],
    so check_sequence's continuity check (unrelated to the budget fix under
    test) never flags these as conflicting."""
    base = dict(
        id=shot_id, scene_id="sc1", description="does something", duration_s=5,
        story_contract_version=1, purpose="purpose", action="action",
        entry_state={"x": f"s{index}"}, exit_state={"x": f"s{index + 1}"},
        transition="cut", cut_reason="",
    )
    base.update(overrides)
    return base


def test_beat_requires_end_after_start_and_non_empty_action():
    Beat(start_s=0, end_s=1.5, action="Raj enters the room")  # valid, does not raise
    with pytest.raises(ValueError, match="end_s"):
        Beat(start_s=2, end_s=2, action="stalled beat")
    with pytest.raises(ValueError, match="action"):
        Beat(start_s=0, end_s=1, action="   ")


def test_shot_defaults_beats_and_cut_reason_for_legacy_construction():
    shot = Shot(id="s1", scene_id="sc1", description="x", duration_s=5)
    assert shot.beats == []
    assert shot.cut_reason == ""


def test_shot_accepts_beats_spanning_its_duration():
    shot = Shot(**_shot("sc1-sh1", beats=[
        Beat(start_s=0, end_s=1.5, action="enters"),
        Beat(start_s=1.5, end_s=5, action="notices the body"),
    ]))
    assert len(shot.beats) == 2
    assert shot.beats[1].action == "notices the body"


class _SingleSceneLLM(MockLLMClient):
    """Two shots in one scene; the second is missing cut_reason."""

    def complete_json(self, *, task, system, user):
        if task == "writer":
            return {"scenes": [dict(id="sc1", slug="s1", title="Scene 1", summary="s",
                                     location_id="loc1", character_ids=["ch1"])]}
        if task == "cinematographer":
            return {"shots": [
                _shot("sc1-sh1", index=0),
                _shot("sc1-sh2", index=1, cut_reason=""),  # missing — should be rejected
            ]}
        return super().complete_json(task=task, system=system, user=user)


def test_cut_reason_required_for_every_shot_after_a_scenes_first():
    with pytest.raises(PipelineError, match="cut_reason"):
        MovieCrew(_SingleSceneLLM()).make("A concept")


class _BudgetLLM(MockLLMClient):
    """Two scenes. sc1's first cinematographer attempt blows the budget
    (10 shots x 5s = 50s against a 30s target); its retry is compliant
    (2 shots totalling 28s). sc2 is compliant on the first attempt."""

    def __init__(self):
        self.cine_calls: list[str] = []

    def complete_json(self, *, task, system, user):
        if task == "writer":
            return {"scenes": [
                dict(id="sc1", slug="s1", title="Scene 1", summary="s", location_id="loc1", character_ids=["ch1"]),
                dict(id="sc2", slug="s2", title="Scene 2", summary="s", location_id="loc1", character_ids=["ch1"]),
            ]}
        if task == "cinematographer":
            scene = json.loads(user)["scene"]
            self.cine_calls.append(scene["id"])
            attempt = sum(1 for s in self.cine_calls if s == scene["id"])
            if scene["id"] == "sc1" and attempt == 1:
                assert scene.get("target_duration_s") == 30
                return {"shots": [
                    _shot(f"sc1-sh{i+1}", index=i, cut_reason="" if i == 0 else "reaction")
                    for i in range(10)  # 10 x 5s = 50s, 1.67x the 30s budget
                ]}
            if scene["id"] == "sc1":
                assert "over_budget_notice" in scene  # the retry saw the corrective note
                return {"shots": [
                    _shot("sc1-sh-r1", index=0, scene_id="sc1", duration_s=14, cut_reason=""),
                    _shot("sc1-sh-r2", index=1, scene_id="sc1", duration_s=14, cut_reason="reveal"),
                ]}
            assert scene.get("target_duration_s") == 30
            return {"shots": [
                _shot("sc2-sh1", index=0, scene_id="sc2", duration_s=15, cut_reason=""),
                _shot("sc2-sh2", index=1, scene_id="sc2", duration_s=15, cut_reason="reveal"),
            ]}
        if task == "prompter":
            shot_id = json.loads(user)["shot"]["id"]
            return {"prompts": [{"shot_id": shot_id, "prompt": f"Placeholder action for {shot_id}.",
                                  "negative_prompt": ""}]}
        return super().complete_json(task=task, system=system, user=user)


def test_target_duration_s_splits_across_scenes_and_retries_when_badly_over():
    llm = _BudgetLLM()
    project = MovieCrew(llm).make("A concept", target_duration_s=60)

    assert project.target_duration_s == 60
    scenes = {s.id: s for s in project.scenes}
    assert scenes["sc1"].target_duration_s == 30
    assert scenes["sc2"].target_duration_s == 30

    # sc1 was replanned once (badly over budget), sc2 never needed a retry.
    assert llm.cine_calls.count("sc1") == 2
    assert llm.cine_calls.count("sc2") == 1

    # The accepted shots are the RETRY's compliant output, not the original
    # 10-shot, 50-second mess — and the old shot ids were freed, not left
    # dangling as phantom duplicates.
    assert [s.id for s in scenes["sc1"].shots] == ["sc1-sh-r1", "sc1-sh-r2"]
    assert sum(s.duration_s for s in scenes["sc1"].shots) == 28
    all_ids = {s.id for scene in project.scenes for s in scene.shots}
    assert "sc1-sh1" not in all_ids

    # A compliant retry (28s against a 30s target) must not itself raise a warning.
    assert not any(f.target == "sc1" for f in project.render_plan.flags)


class _StillOverAfterRetryLLM(MockLLMClient):
    """Both the first attempt AND the retry blow the budget."""

    def complete_json(self, *, task, system, user):
        if task == "writer":
            return {"scenes": [dict(id="sc1", slug="s1", title="Scene 1", summary="s",
                                     location_id="loc1", character_ids=["ch1"])]}
        if task == "cinematographer":
            return {"shots": [
                _shot(f"sc1-sh{i+1}", index=i, cut_reason="" if i == 0 else "reaction")
                for i in range(10)  # 50s every time, against a 10s target
            ]}
        if task == "prompter":
            shot_id = json.loads(user)["shot"]["id"]
            return {"prompts": [{"shot_id": shot_id, "prompt": f"Placeholder action for {shot_id}.",
                                  "negative_prompt": ""}]}
        return super().complete_json(task=task, system=system, user=user)


def test_still_over_budget_after_one_retry_warns_but_does_not_crash():
    project = MovieCrew(_StillOverAfterRetryLLM()).make("A concept", target_duration_s=10)
    scene = project.scenes[0]
    assert sum(s.duration_s for s in scene.shots) == 50  # accepted anyway — a warning, not a hard failure
    warnings = [f for f in project.render_plan.flags if f.target == scene.id and f.kind == "warning"]
    assert warnings and "budget" not in warnings[0].message  # message names the overage, doesn't need the word
    assert any("target" in f.message for f in warnings)
    # The film-level rollup warns too, since the scene-level fix didn't land.
    assert any(f.target == "project" and "Planned runtime" in f.message for f in project.render_plan.flags)


def test_no_target_duration_s_means_zero_budget_checks_ever_run():
    llm = _StillOverAfterRetryLLM()
    project = MovieCrew(llm).make("A concept")  # target_duration_s omitted entirely
    assert project.target_duration_s is None
    assert project.scenes[0].target_duration_s is None
    assert not any(f.kind == "warning" and "target" in f.message for f in project.render_plan.flags)


def test_beats_round_trip_through_project_save_and_load(tmp_path, monkeypatch):
    from moviecrew import projects
    from moviecrew.image import MockImageProvider
    from moviecrew.studio import StudioSession, Stage

    monkeypatch.setenv("MOVIECREW_PROJECTS_ROOT", str(tmp_path / "db"))
    llm = _SingleSceneLLM()
    # Bypass the cut_reason rejection this LLM is designed to trigger —
    # only its writer/cinematographer shape (with beats added) is wanted here.

    class WithBeats(_SingleSceneLLM):
        def complete_json(self, *, task, system, user):
            if task == "cinematographer":
                return {"shots": [
                    _shot("sc1-sh1", beats=[
                        {"start_s": 0, "end_s": 2, "action": "enters"},
                        {"start_s": 2, "end_s": 5, "action": "notices the body"},
                    ]),
                ]}
            return MockLLMClient.complete_json(self, task=task, system=system, user=user)

    session = StudioSession("beats-project", Stage.SHOT_DEFS,
                             MovieCrew(WithBeats()).make("A concept"),
                             str(tmp_path / "media"), MockImageProvider())
    projects.save(session)
    restored = projects.load("beats-project", MockImageProvider())

    shot = restored.project.scenes[0].shots[0]
    assert len(shot.beats) == 2
    assert all(isinstance(b, Beat) for b in shot.beats)
    assert shot.beats[1].action == "notices the body"


class _MicroShotLLM(MockLLMClient):
    """First attempt has shots under the pacing floor; the retry is compliant."""

    def __init__(self):
        self.cine_calls = 0

    def complete_json(self, *, task, system, user):
        if task == "writer":
            return {"scenes": [dict(id="sc1", slug="s1", title="Scene 1", summary="s",
                                     location_id="loc1", character_ids=["ch1"])]}
        if task == "cinematographer":
            self.cine_calls += 1
            if self.cine_calls == 1:
                return {"shots": [
                    _shot("sc1-sh1", index=0, duration_s=2, cut_reason=""),
                    _shot("sc1-sh2", index=1, duration_s=2.5, cut_reason="reaction"),
                ]}
            return {"shots": [
                _shot("sc1-sh1r", index=0, scene_id="sc1", duration_s=6, cut_reason=""),
                _shot("sc1-sh2r", index=1, scene_id="sc1", duration_s=7, cut_reason="reaction"),
            ]}
        if task == "prompter":
            shot_id = json.loads(user)["shot"]["id"]
            return {"prompts": [{"shot_id": shot_id, "prompt": f"Placeholder for {shot_id}.",
                                  "negative_prompt": ""}]}
        return super().complete_json(task=task, system=system, user=user)


def test_shots_under_the_pacing_floor_trigger_one_retry_then_succeed():
    llm = _MicroShotLLM()
    project = MovieCrew(llm).make("A concept")  # no target_duration_s at all — pacing still applies

    assert llm.cine_calls == 2
    scene = project.scenes[0]
    assert [s.duration_s for s in scene.shots] == [6, 7]
    assert not any(f.target == "sc1" for f in project.render_plan.flags)


class _StillMicroAfterRetryLLM(MockLLMClient):
    """Both attempts stay outside the pacing policy; the guardrail clamps."""

    def complete_json(self, *, task, system, user):
        if task == "writer":
            return {"scenes": [dict(id="sc1", slug="s1", title="Scene 1", summary="s",
                                     location_id="loc1", character_ids=["ch1"])]}
        if task == "cinematographer":
            return {"shots": [
                _shot("sc1-sh1", index=0, duration_s=2, cut_reason=""),
                _shot("sc1-sh2", index=1, duration_s=20, cut_reason="reaction"),
            ]}
        if task == "prompter":
            shot_id = json.loads(user)["shot"]["id"]
            return {"prompts": [{"shot_id": shot_id, "prompt": f"Placeholder for {shot_id}.",
                                  "negative_prompt": ""}]}
        return super().complete_json(task=task, system=system, user=user)


def test_shots_still_out_of_range_after_retry_are_clamped_and_flagged():
    project = MovieCrew(_StillMicroAfterRetryLLM()).make("A concept")
    scene = project.scenes[0]
    durations = {s.id: s.duration_s for s in scene.shots}
    assert durations["sc1-sh1"] == MIN_SHOT_DURATION_S  # clamped up to the floor
    assert durations["sc1-sh2"] == MAX_SHOT_DURATION_S  # clamped down to the ceiling
    warnings = [f for f in project.render_plan.flags if f.target == scene.id and f.kind == "warning"]
    assert warnings and "clamped" in warnings[0].message


class _BudgetAndPacingLLM(MockLLMClient):
    """A scene that is both over budget and has out-of-range shots on attempt
    one; both problems must be described in the SAME single retry, and the
    retry's own leftover pacing violation still gets clamped afterward."""

    def __init__(self):
        self.cine_calls = 0

    def complete_json(self, *, task, system, user):
        if task == "writer":
            return {"scenes": [dict(id="sc1", slug="s1", title="Scene 1", summary="s",
                                     location_id="loc1", character_ids=["ch1"])]}
        if task == "cinematographer":
            self.cine_calls += 1
            scene = json.loads(user)["scene"]
            if self.cine_calls == 1:
                assert "over_budget_notice" not in scene
                return {"shots": [
                    _shot("sc1-sh1", index=0, duration_s=2, cut_reason=""),
                    _shot("sc1-sh2", index=1, duration_s=20, cut_reason="reaction"),
                    _shot("sc1-sh3", index=2, duration_s=20, cut_reason="reaction"),
                ]}  # 42s total against a 10s target, and every shot out of range
            notice = scene["over_budget_notice"]
            assert "budget" in notice.lower()
            assert "between 5 and 15" in notice
            return {"shots": [
                _shot("sc1-sh1r", index=0, scene_id="sc1", duration_s=6, cut_reason=""),
                _shot("sc1-sh2r", index=1, scene_id="sc1", duration_s=4, cut_reason="reaction"),
            ]}
        if task == "prompter":
            shot_id = json.loads(user)["shot"]["id"]
            return {"prompts": [{"shot_id": shot_id, "prompt": f"Placeholder for {shot_id}.",
                                  "negative_prompt": ""}]}
        return super().complete_json(task=task, system=system, user=user)


def test_budget_overage_and_pacing_violation_share_a_single_retry():
    llm = _BudgetAndPacingLLM()
    project = MovieCrew(llm).make("A concept", target_duration_s=10)

    assert llm.cine_calls == 2  # one retry covers both problems, not two
    scene = project.scenes[0]
    durations = {s.id: s.duration_s for s in scene.shots}
    assert durations == {"sc1-sh1r": 6, "sc1-sh2r": MIN_SHOT_DURATION_S}  # sh2r's 4s clamped up

    warnings = [f for f in project.render_plan.flags if f.target == scene.id]
    assert any("clamped" in w.message for w in warnings)
    assert not any("budget" in w.message.lower() for w in warnings)  # 10s retotal is within the 15s budget tolerance
