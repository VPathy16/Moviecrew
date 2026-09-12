"""End-to-end tests that creative intent survives the whole pipeline.

Dataclass tests prove a field exists. These prove the invariant: what the
filmmaker asked for reaches the execution boundary unchanged, and only the
adapter decides how much of it a given backend can honour.

Everything runs offline on scripted LLM output, so each test states exactly
what the agents returned and exactly what should have survived.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from moviecrew.crew import MovieCrew, PipelineError
from moviecrew.llm import LLMClient
from moviecrew.production import resolve_shot
from moviecrew.render import ShotSpec
from moviecrew.rules import normalize_order
from moviecrew.schema import Shot
from moviecrew.video import (
    VEO_LEGAL_DURATIONS_S,
    VEO_MAX_CHAIN_SEGMENTS,
    VEO_MAX_REFERENCE_IMAGES,
    segment_for_veo,
    veo_prompt,
)


class ScriptedLLM(LLMClient):
    """An LLM whose every answer is stated by the test that uses it."""

    def __init__(self, **by_task):
        self.by_task = by_task
        self.calls: list[str] = []

    def complete_json(self, *, task, system, user):
        self.calls.append(task)
        answer = self.by_task[task]
        return answer(json.loads(user)) if callable(answer) else answer


def _base_script(**overrides):
    """A minimal one-scene, two-shot project the tests vary from."""
    script = {
        "director": {
            "title": "Salt",
            "logline": "A keeper outlasts a storm.",
            "outline": ["The storm arrives."],
        },
        "writer": {
            "scenes": [
                {
                    "id": "sc1",
                    "slug": "lighthouse",
                    "title": "The Lighthouse",
                    "summary": "Mara climbs.",
                    "character_ids": ["ch1"],
                }
            ]
        },
        "designer": {
            "style": "grim",
            "palette": "cold",
            "mood": "tense",
            "characters": [
                {"id": "ch1", "name": "Mara", "description": "keeper", "reference_images": []}
            ],
            "locations": [],
            "props": [],
        },
        "cinematographer": {
            "shots": [
                {
                    "id": "sc1-sh1",
                    "scene_id": "sc1",
                    "description": "Mara climbs.",
                    "duration_s": 8,
                    "camera_move": "slow push-in",
                    "lens": "35mm",
                    "framing": "wide",
                },
                {
                    "id": "sc1-sh2",
                    "scene_id": "sc1",
                    "description": "The lamp turns.",
                    "duration_s": 8,
                    "camera_move": "static",
                    "lens": "50mm",
                    "framing": "close",
                },
            ]
        },
        "editor": {"order": ["sc1-sh1", "sc1-sh2"], "chains": [["sc1-sh1", "sc1-sh2"]]},
        "prompter": lambda payload: {
            "prompts": [
                {
                    "shot_id": payload["shot"]["id"],
                    "prompt": f"A prompt for {payload['shot']['id']}.",
                    "negative_prompt": "blurry",
                }
            ]
        },
        "continuity": {"flags": []},
    }
    script.update(overrides)
    return script


def _make(**overrides):
    return MovieCrew(ScriptedLLM(**_base_script(**overrides))).make("A storm.")


# ---------------------------------------------------------------------- #
# 1. An unusual duration survives to the intent                           #
# ---------------------------------------------------------------------- #


def test_a_cinematographer_duration_of_11_5_reaches_the_intent():
    cine = _base_script()["cinematographer"]
    cine["shots"][0]["duration_s"] = 11.5

    project = _make(cinematographer=cine)

    shot = next(s for sc in project.scenes for s in sc.shots if s.id == "sc1-sh1")
    intent = next(i for i in project.render_plan.intents if i.shot_id == "sc1-sh1")

    assert shot.duration_s == 11.5
    assert intent.duration_s == 11.5
    assert intent.duration_s not in VEO_LEGAL_DURATIONS_S


@pytest.mark.parametrize("duration", [2.5, 5, 11.5, 18])
def test_a_range_of_intended_durations_all_survive(duration):
    cine = _base_script()["cinematographer"]
    cine["shots"][0]["duration_s"] = duration
    project = _make(cinematographer=cine)
    intent = next(i for i in project.render_plan.intents if i.shot_id == "sc1-sh1")
    assert intent.duration_s == duration


def test_the_veo_adapter_clamps_that_duration_without_touching_the_intent():
    cine = _base_script()["cinematographer"]
    cine["shots"][0]["duration_s"] = 11.5
    project = _make(cinematographer=cine)
    intent = next(i for i in project.render_plan.intents if i.shot_id == "sc1-sh1")

    prompt = veo_prompt(intent)

    assert prompt.duration_s in VEO_LEGAL_DURATIONS_S
    assert intent.duration_s == 11.5


# ---------------------------------------------------------------------- #
# 2-3. Five references survive; the adapter takes three                   #
# ---------------------------------------------------------------------- #


def test_five_references_survive_to_execution_and_veo_takes_three(tmp_path):
    refs = [str(tmp_path / f"ref{n}.png") for n in range(5)]
    for ref in refs:
        Path(ref).write_bytes(b"png")
    designer = _base_script()["designer"]
    designer["characters"][0]["reference_images"] = refs

    project = MovieCrew(
        ScriptedLLM(**_base_script(designer=designer)),
    ).make("A storm.")

    head = next(s for sc in project.scenes for s in sc.shots if s.consistency_anchor)
    assert len(head.reference_image_ids) == 5, "anchoring must not truncate"

    state = resolve_shot(project, head.id)
    assert state.reference_images == refs

    prompt = veo_prompt(state.intent, reference_images=state.reference_images)
    assert len(prompt.reference_images) == VEO_MAX_REFERENCE_IMAGES
    assert head.reference_image_ids == refs, "adapting must not mutate the shot"


# ---------------------------------------------------------------------- #
# 4-5. A creative chain longer than Veo's limit                           #
# ---------------------------------------------------------------------- #


def _long_take_script(length: int):
    shot_ids = [f"sc1-sh{n}" for n in range(length)]
    cine = {
        "shots": [
            {
                "id": shot_id,
                "scene_id": "sc1",
                "description": f"beat {n}",
                "duration_s": 4,
                "camera_move": "handheld",
                "lens": "24mm",
                "framing": "medium",
            }
            for n, shot_id in enumerate(shot_ids)
        ]
    }
    editor = {"order": shot_ids, "chains": [shot_ids]}
    return shot_ids, cine, editor


def test_a_take_longer_than_veo_can_execute_stays_whole_in_the_plan():
    length = VEO_MAX_CHAIN_SEGMENTS + 5
    shot_ids, cine, editor = _long_take_script(length)

    project = _make(cinematographer=cine, editor=editor)

    assert project.render_plan.chains == [shot_ids]
    assert len(project.render_plan.chains[0]) > VEO_MAX_CHAIN_SEGMENTS


def test_veo_segments_that_take_at_the_execution_boundary():
    length = VEO_MAX_CHAIN_SEGMENTS + 5
    shot_ids, cine, editor = _long_take_script(length)
    project = _make(cinematographer=cine, editor=editor)

    runs = segment_for_veo(project.render_plan.chains[0])

    assert len(runs) == 2
    assert [shot_id for run in runs for shot_id in run] == shot_ids
    assert project.render_plan.chains == [shot_ids], "segmenting must not mutate the plan"


def test_each_veo_run_restarts_from_its_own_base_clip():
    """The 22nd shot of a 26-shot take cannot extend from the 21st — Veo's
    run has ended. It starts a new base clip instead."""
    from moviecrew.video import StubVideoBackend

    length = VEO_MAX_CHAIN_SEGMENTS + 5
    shot_ids, cine, editor = _long_take_script(length)
    project = _make(cinematographer=cine, editor=editor)

    results = MovieCrew(ScriptedLLM()).render(project, StubVideoBackend())
    extend_from = {r.shot_id: r.raw["extend_from"] for r in results}

    assert extend_from[shot_ids[0]] is None
    assert extend_from[shot_ids[1]] == shot_ids[0]
    assert extend_from[shot_ids[VEO_MAX_CHAIN_SEGMENTS]] is None, "new run, new base clip"
    assert extend_from[shot_ids[VEO_MAX_CHAIN_SEGMENTS + 1]] == shot_ids[VEO_MAX_CHAIN_SEGMENTS]


# ---------------------------------------------------------------------- #
# 6. Storyboard approval reaches the actual request                       #
# ---------------------------------------------------------------------- #


def test_storyboard_approval_changes_what_the_render_request_receives(tmp_path):
    """The regression this architecture exists to prevent: an intent built at
    plan time, a board approved afterwards, and a render that went out
    anchored to the wrong stills."""
    from moviecrew.image import MockImageProvider
    from moviecrew.studio import Stage, StudioSession

    class Promoting(MockImageProvider):
        promotes_references = True

    library = tmp_path / "library.png"
    library.write_bytes(b"png")
    designer = _base_script()["designer"]
    designer["characters"][0]["reference_images"] = [str(library)]
    project = _make(designer=designer)

    head = next(s for sc in project.scenes for s in sc.shots if s.consistency_anchor)
    before = resolve_shot(project, head.id).reference_images
    assert before == [str(library)]

    session = StudioSession(
        session_id="s",
        stage=Stage.SHOT_DEFS,
        project=project,
        session_dir=str(tmp_path),
        image_provider=Promoting(),
    )
    session.produce()
    session.approve()

    after = resolve_shot(project, head.id).reference_images
    assert after[0] != str(library), "the approved board image is now first"
    assert str(library) in after, "the library still is kept, not discarded"
    assert after != before

    # And it reaches the request a backend would actually be sent.
    spec = ShotSpec.from_intent(
        resolve_shot(project, head.id).intent, reference_images=after
    )
    assert spec.reference_images == after


# ---------------------------------------------------------------------- #
# 8. Editor output is normalized deterministically                        #
# ---------------------------------------------------------------------- #


def _shots(*ids):
    return [Shot(id=i, scene_id="sc1", description="d", duration_s=4) for i in ids]


def test_normalize_order_drops_unknown_ids():
    assert normalize_order(_shots("a", "b"), ["a", "ghost", "b"]) == ["a", "b"]


def test_normalize_order_collapses_duplicates():
    assert normalize_order(_shots("a", "b"), ["a", "a", "b", "a"]) == ["a", "b"]


def test_normalize_order_appends_shots_the_editor_forgot():
    assert normalize_order(_shots("a", "b", "c"), ["c", "a"]) == ["c", "a", "b"]


def test_normalize_order_keeps_the_editors_ordering_where_valid():
    assert normalize_order(_shots("a", "b", "c"), ["c", "b", "a"]) == ["c", "b", "a"]


def test_normalize_order_survives_an_empty_proposal():
    assert normalize_order(_shots("a", "b"), []) == ["a", "b"]


def test_every_shot_appears_exactly_once_end_to_end():
    editor = {"order": ["sc1-sh2", "sc1-sh2", "ghost"], "chains": [["ghost"]]}
    project = _make(editor=editor)

    order = project.render_plan.order
    all_ids = [s.id for sc in project.scenes for s in sc.shots]

    assert sorted(order) == sorted(all_ids)
    assert len(order) == len(set(order))
    chained = [i for chain in project.render_plan.chains for i in chain]
    assert sorted(chained) == sorted(all_ids)


# ---------------------------------------------------------------------- #
# 9. Nothing disappears silently                                          #
# ---------------------------------------------------------------------- #


def test_a_prompter_answering_for_the_wrong_shot_raises():
    """It used to filter to zero rows and move on, leaving a shot in the film
    with no intent behind it."""
    def wrong_shot(payload):
        return {"prompts": [{"shot_id": "some-other-shot", "prompt": "x"}]}

    with pytest.raises(PipelineError, match="no prompt for shot"):
        _make(prompter=wrong_shot)


def test_a_prompter_returning_nothing_raises():
    with pytest.raises(PipelineError, match="no prompt for shot"):
        _make(prompter={"prompts": []})


def test_a_prompter_answer_missing_the_prompt_field_raises():
    def no_text(payload):
        return {"prompts": [{"shot_id": payload["shot"]["id"]}]}

    with pytest.raises(PipelineError, match="no 'prompt' field"):
        _make(prompter=no_text)


def test_extra_prompts_for_other_shots_are_flagged_not_fatal():
    def noisy(payload):
        return {
            "prompts": [
                {"shot_id": payload["shot"]["id"], "prompt": "mine"},
                {"shot_id": "somebody-else", "prompt": "theirs"},
            ]
        }

    project = _make(prompter=noisy)
    assert len(project.render_plan.intents) == 2
    assert any("unrelated shots" in f.message for f in project.render_plan.flags)


def test_a_cinematographer_shot_for_another_scene_raises():
    cine = _base_script()["cinematographer"]
    cine["shots"][1]["scene_id"] = "sc9"
    with pytest.raises(PipelineError, match="scene_id"):
        _make(cinematographer=cine)


def test_duplicate_shot_ids_raise():
    cine = _base_script()["cinematographer"]
    cine["shots"][1]["id"] = cine["shots"][0]["id"]
    with pytest.raises(PipelineError, match="duplicate shot id"):
        _make(cinematographer=cine)


def test_a_scene_with_no_shots_raises():
    with pytest.raises(PipelineError, match="no shots for scene"):
        _make(cinematographer={"shots": []})


# ---------------------------------------------------------------------- #
# Extra fields the cinematographer adds beyond the schema are ignored     #
# ---------------------------------------------------------------------- #


def test_a_shot_with_an_extra_note_field_succeeds():
    """The bug report this guards against: Shot.__init__() got an
    unexpected keyword argument 'note', from a shot that was otherwise
    perfectly valid."""
    cine = _base_script()["cinematographer"]
    cine["shots"][0]["note"] = "consider a handheld feel here"
    project = _make(cinematographer=cine)
    assert len(project.render_plan.intents) == 2


def test_several_extra_fields_together_succeed():
    cine = _base_script()["cinematographer"]
    cine["shots"][0]["note"] = "a note"
    cine["shots"][0]["rationale"] = "why this shot exists"
    cine["shots"][1]["transition"] = "hard cut"
    cine["shots"][1]["comments"] = "reviewer feedback"
    project = _make(cinematographer=cine)
    assert len(project.render_plan.intents) == 2


def test_an_extra_field_does_not_get_added_to_the_built_shot():
    """Dropped, not carried through as an attribute on the domain object —
    the fix filters at the boundary, it does not widen Shot."""
    cine = _base_script()["cinematographer"]
    cine["shots"][0]["note"] = "should not survive"
    project = _make(cinematographer=cine)
    shot = next(
        s for scene in project.scenes for s in scene.shots if s.id == "sc1-sh1"
    )
    assert not hasattr(shot, "note")


@pytest.mark.parametrize("missing_field", ["id", "scene_id", "description", "duration_s"])
def test_a_shot_missing_a_required_field_raises_a_useful_pipeline_error(missing_field):
    cine = _base_script()["cinematographer"]
    del cine["shots"][0][missing_field]
    with pytest.raises(PipelineError) as excinfo:
        _make(cinematographer=cine)
    message = str(excinfo.value)
    assert "missing required field" in message
    assert missing_field in message
    # Never a bare TypeError escaping from Shot(**shot_data).
    assert excinfo.type is PipelineError


def test_a_missing_required_field_names_the_scene():
    cine = _base_script()["cinematographer"]
    del cine["shots"][0]["duration_s"]
    with pytest.raises(PipelineError, match="sc1"):
        _make(cinematographer=cine)


# ---------------------------------------------------------------------- #
# Continuity failing must never cost the plan already generated           #
# ---------------------------------------------------------------------- #


def _raising(exc: Exception):
    """A ScriptedLLM answer that raises instead of returning JSON."""

    def _raise(payload):
        raise exc

    return _raise


def test_a_continuity_exception_still_returns_a_project():
    """The bug report this guards against: a large project generated every
    scene/shot/prompt, then the continuity call failed and the whole plan
    was lost. It must not be, regardless of what continuity raises."""
    project = _make(continuity=_raising(RuntimeError("connection reset")))
    assert project.title == "Salt"
    assert len(project.scenes) == 1
    assert len(project.render_plan.intents) == 2


def test_a_continuity_exception_appends_a_project_level_warning():
    project = _make(continuity=_raising(RuntimeError("connection reset")))
    warnings = [f for f in project.render_plan.flags if f.target == "project"]
    assert len(warnings) == 1
    assert warnings[0].kind == "warning"
    assert "connection reset" in warnings[0].message


def test_a_truncated_continuity_response_still_returns_a_project():
    """The literal failure reported: finish_reason="length" surfaces as an
    LLMError from the real client; here it's simulated directly, since the
    point under test is what crew.make() does with it, not how the
    OpenRouter client detects it (see llm_openrouter.py for that)."""
    from moviecrew.llm_openrouter import LLMError

    truncation = LLMError(
        "anthropic/claude-sonnet-5 output for task 'continuity' was "
        "truncated (finish_reason='length') before valid JSON completed"
    )
    project = _make(continuity=_raising(truncation))
    assert project.title == "Salt"
    assert len(project.render_plan.intents) == 2
    warnings = [f for f in project.render_plan.flags if f.target == "project"]
    assert "truncated" in warnings[0].message


def test_malformed_continuity_output_still_returns_a_project():
    """A response that parsed as JSON but not into the expected shape — no
    "flags" key at all — must be treated the same as any other continuity
    failure, not crash on continuity_out["flags"]."""
    project = _make(continuity={"oops": "not the expected shape"})
    assert project.title == "Salt"
    assert len(project.render_plan.intents) == 2
    warnings = [f for f in project.render_plan.flags if f.target == "project"]
    assert len(warnings) == 1
    assert "KeyError" in warnings[0].message


def test_continuity_failure_does_not_lose_other_flags():
    """A project-level warning is added to the existing flags, not swapped
    in for them — a warning computed before continuity ever ran (here, the
    prompter-returned-prompts-for-unrelated-shots flag) must still be
    there."""

    def noisy(payload):
        return {
            "prompts": [
                {"shot_id": payload["shot"]["id"], "prompt": "mine"},
                {"shot_id": "somebody-else", "prompt": "theirs"},
            ]
        }

    project = _make(prompter=noisy, continuity=_raising(RuntimeError("boom")))
    assert any(f.target == "project" for f in project.render_plan.flags)
    assert any("unrelated shots" in f.message for f in project.render_plan.flags)


def test_continuity_success_is_unaffected_by_the_failure_handling():
    """The ordinary path — continuity returns real flags — must look
    exactly as it did before this change."""
    project = _make()
    assert not any(f.target == "project" for f in project.render_plan.flags)


def test_checkpoint_is_written_before_continuity_runs(tmp_path):
    """The other half of the data-loss fix: even if something below this
    point were to crash in a way no exception handler catches, the plan
    generated so far already exists on disk."""
    checkpoint = tmp_path / "session" / "checkpoint.json"
    crew = MovieCrew(ScriptedLLM(**_base_script(continuity=_raising(RuntimeError("boom")))))

    project = crew.make("A storm.", checkpoint_path=str(checkpoint))

    assert checkpoint.is_file()
    saved = json.loads(checkpoint.read_text())
    assert saved["title"] == project.title
    assert len(saved["scenes"][0]["shots"]) == 2
    # Written before continuity ran, so it must not carry continuity's
    # failure warning — that is appended to the in-memory Project only
    # after the checkpoint was already on disk.
    assert not any(f["target"] == "project" for f in saved["render_plan"]["flags"])


def test_checkpoint_is_written_even_though_continuity_later_fails():
    """Confirms the write happens regardless of what continuity does next —
    tested separately from the content check above, on the success path."""
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as d:
        checkpoint = Path(d) / "checkpoint.json"
        crew = MovieCrew(
            ScriptedLLM(**_base_script(continuity=_raising(RuntimeError("boom"))))
        )
        crew.make("A storm.", checkpoint_path=str(checkpoint))
        assert checkpoint.is_file()


def test_a_bad_checkpoint_path_does_not_fail_plan_generation():
    """A checkpoint that cannot be written (here: a path through a file,
    not a directory) must not itself take down plan generation — that would
    be the exact failure this patch exists to prevent, self-inflicted."""
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as d:
        blocked = Path(d) / "not-a-directory"
        blocked.write_text("occupying this path")
        bad_checkpoint = blocked / "checkpoint.json"

        crew = MovieCrew(ScriptedLLM(**_base_script()))
        project = crew.make("A storm.", checkpoint_path=str(bad_checkpoint))

    assert project.title == "Salt"


def test_every_shot_gets_exactly_one_intent():
    project = _make()
    shot_ids = [s.id for sc in project.scenes for s in sc.shots]
    intent_ids = [i.shot_id for i in project.render_plan.intents]
    assert sorted(intent_ids) == sorted(shot_ids)
    assert len(intent_ids) == len(set(intent_ids))
