"""Tests for the canonical production objects and the execution boundary.

The invariant under test throughout: MovieCrew preserves what the filmmaker
asked for, and a backend adapter decides how much of that a given execution
system can honour. A constraint that leaks upstream of an adapter destroys
information before anyone has chosen what will render the shot.
"""

from __future__ import annotations

import pytest

from moviecrew.production import ShotState, UnknownShot, resolve_shot
from moviecrew.render import ShotSpec
from moviecrew.schema import (
    Bible,
    Project,
    RenderPlan,
    Scene,
    Shot,
    ShotIntent,
    parse_aspect_ratio,
)
from moviecrew.video import (
    VEO_LEGAL_DURATIONS_S,
    VEO_MAX_CHAIN_SEGMENTS,
    VEO_MAX_REFERENCE_IMAGES,
    VeoPrompt,
    segment_for_veo,
    veo_prompt,
)


def _project(shot, intent=None):
    scene = Scene(id=shot.scene_id, slug="s", title="t", summary="s", shots=[shot])
    return Project(
        title="t",
        logline="l",
        bible=Bible(style="s", palette="p", mood="m"),
        scenes=[scene],
        render_plan=RenderPlan(intents=[intent] if intent else []),
    )


# ---------------------------------------------------------------------- #
# Shot: production intent, not backend capability                         #
# ---------------------------------------------------------------------- #


def test_shot_duration_is_not_snapped():
    """2.5s is not a legal Veo clip and is an ordinary creative intention."""
    shot = Shot(id="s1", scene_id="sc1", description="d", duration_s=2.5)
    assert shot.duration_s == 2.5
    assert shot.duration_s not in VEO_LEGAL_DURATIONS_S


def test_shot_accepts_a_long_duration():
    assert Shot(id="s1", scene_id="sc1", description="d", duration_s=18).duration_s == 18


def test_shot_references_are_uncapped():
    refs = [f"ref{n}.png" for n in range(VEO_MAX_REFERENCE_IMAGES + 2)]
    shot = Shot(id="s1", scene_id="sc1", description="d", duration_s=8, reference_image_ids=refs)
    assert shot.reference_image_ids == refs


@pytest.mark.parametrize("bad", [0, -1, -0.5])
def test_shot_rejects_a_nonpositive_duration(bad):
    with pytest.raises(ValueError, match="positive"):
        Shot(id="s1", scene_id="sc1", description="d", duration_s=bad)


# ---------------------------------------------------------------------- #
# ShotIntent                                                              #
# ---------------------------------------------------------------------- #


def test_intent_duration_is_not_snapped():
    assert ShotIntent(shot_id="s1", description="a walk", duration_s=11.5).duration_s == 11.5


@pytest.mark.parametrize("bad", [0, -3])
def test_intent_rejects_a_nonpositive_duration(bad):
    with pytest.raises(ValueError, match="positive"):
        ShotIntent(shot_id="s1", description="d", duration_s=bad)


def test_intent_carries_no_reference_images():
    """References live on the Shot. A second mutable copy is how a canonical
    representation stops being canonical."""
    assert not hasattr(ShotIntent(shot_id="s1", description="d"), "reference_images")


@pytest.mark.parametrize("ratio", ["16:9", "9:16", "239:100", "1:1", "4:3"])
def test_any_real_ratio_is_expressible(ratio):
    """2.39:1 anamorphic is a legitimate thing for a film to want."""
    assert ShotIntent(shot_id="s1", description="d", aspect_ratio=ratio).aspect_ratio == ratio


@pytest.mark.parametrize("ratio", ["0:0", "16:0", "0:9"])
def test_degenerate_ratios_are_refused(ratio):
    """Well-formed strings, meaningless as ratios — caught before a backend
    turns one into a division by zero."""
    with pytest.raises(ValueError, match="positive"):
        ShotIntent(shot_id="s1", description="d", aspect_ratio=ratio)


@pytest.mark.parametrize("ratio", ["widescreen", "16-9", "16:9:1", "", "16:", ":9", "1.85:1"])
def test_malformed_ratios_are_refused(ratio):
    with pytest.raises(ValueError, match="W:H"):
        ShotIntent(shot_id="s1", description="d", aspect_ratio=ratio)


def test_parse_aspect_ratio_returns_both_sides():
    assert parse_aspect_ratio("239:100") == (239, 100)


# ---------------------------------------------------------------------- #
# The Veo adapter is the only place Veo's limits apply                    #
# ---------------------------------------------------------------------- #


def test_adapter_snaps_the_duration():
    assert veo_prompt(
        ShotIntent(shot_id="s1", description="d", duration_s=11.5)
    ).duration_s in VEO_LEGAL_DURATIONS_S


def test_adapter_truncates_references_to_veo_s_cap():
    refs = [f"ref{n}.png" for n in range(VEO_MAX_REFERENCE_IMAGES + 2)]
    prompt = veo_prompt(ShotIntent(shot_id="s1", description="d"), reference_images=refs)
    assert prompt.reference_images == refs[:VEO_MAX_REFERENCE_IMAGES]


def test_adapting_leaves_the_intent_intact():
    """What was asked for stays recoverable after a request that could not
    honour it — the whole reason intent and request are separate objects."""
    intent = ShotIntent(shot_id="s1", description="d", duration_s=11.5)
    veo_prompt(intent, reference_images=["a.png", "b.png", "c.png", "d.png"])
    assert intent.duration_s == 11.5


def test_adapter_carries_the_text_across():
    intent = ShotIntent(shot_id="sc1-sh1", description="Mara climbs.", negative="blurry, text")
    prompt = veo_prompt(intent)
    assert prompt.shot_id == "sc1-sh1"
    assert prompt.prompt == "Mara climbs."
    assert prompt.negative_prompt == "blurry, text"


def test_adapter_refuses_a_ratio_veo_cannot_render():
    """Rejected at the boundary, where it is actionable — not at plan time,
    where it would have blocked writing the shot at all."""
    with pytest.raises(ValueError, match="aspect_ratio"):
        veo_prompt(ShotIntent(shot_id="s1", description="d", aspect_ratio="239:100"))


def test_veo_is_unknown_to_the_schema():
    """The shared vocabulary should not need to know a vendor named Veo."""
    import moviecrew.schema as schema

    assert not hasattr(schema, "VeoPrompt")
    assert not [name for name in vars(schema) if name.startswith("VEO_")]
    assert isinstance(veo_prompt(ShotIntent(shot_id="s", description="d")), VeoPrompt)


# ---------------------------------------------------------------------- #
# Editorial chains vs backend execution runs                              #
# ---------------------------------------------------------------------- #


def test_segment_for_veo_splits_a_long_take_into_runs():
    chain = [f"s{i}" for i in range(VEO_MAX_CHAIN_SEGMENTS + 5)]
    runs = segment_for_veo(chain)
    assert len(runs) == 2
    assert runs[0] == chain[:VEO_MAX_CHAIN_SEGMENTS]
    assert runs[1] == chain[VEO_MAX_CHAIN_SEGMENTS:]
    assert [shot_id for run in runs for shot_id in run] == chain


def test_segment_for_veo_leaves_a_short_take_whole():
    assert segment_for_veo(["a", "b"]) == [["a", "b"]]


def test_segmenting_does_not_mutate_the_chain():
    chain = [f"s{i}" for i in range(VEO_MAX_CHAIN_SEGMENTS + 3)]
    before = list(chain)
    segment_for_veo(chain)
    assert chain == before


# ---------------------------------------------------------------------- #
# Resolving live production state                                         #
# ---------------------------------------------------------------------- #


def test_resolve_shot_reads_references_from_the_shot_not_a_copy():
    shot = Shot(
        id="s1", scene_id="sc1", description="d", duration_s=8, reference_image_ids=["a.png"]
    )
    project = _project(shot, ShotIntent(shot_id="s1", description="written by the prompter"))

    shot.reference_image_ids = ["approved.png", "a.png"]  # as storyboard approval would
    state = resolve_shot(project, "s1")

    assert state.reference_images == ["approved.png", "a.png"]
    assert state.intent.description == "written by the prompter"


def test_resolve_shot_falls_back_to_the_shot_before_the_prompter_has_run():
    shot = Shot(id="s1", scene_id="sc1", description="Mara on the cliff", duration_s=5)
    state = resolve_shot(_project(shot), "s1")
    assert state.intent.description == "Mara on the cliff"
    assert state.intent.duration_s == 5


def test_resolve_shot_rejects_an_unknown_shot():
    shot = Shot(id="s1", scene_id="sc1", description="d", duration_s=8)
    with pytest.raises(UnknownShot, match="s404"):
        resolve_shot(_project(shot), "s404")


def test_shot_state_is_a_read_only_view():
    shot = Shot(id="s1", scene_id="sc1", description="d", duration_s=8)
    state = resolve_shot(_project(shot), "s1")
    assert isinstance(state, ShotState)
    with pytest.raises(Exception):
        state.intent = ShotIntent(shot_id="s1", description="other")


# ---------------------------------------------------------------------- #
# One intent, many adapters                                               #
# ---------------------------------------------------------------------- #


def test_one_intent_feeds_both_adapters():
    intent = ShotIntent(shot_id="sc1-sh1", description="Mara climbs.", negative="blurry")
    refs = ["mara.png"]

    veo = veo_prompt(intent, reference_images=refs)
    spec = ShotSpec.from_intent(intent, reference_images=refs)

    assert veo.prompt == spec.prompt == intent.description
    assert veo.negative_prompt == spec.negative_prompt == intent.negative
    assert veo.reference_images == spec.reference_images == refs


def test_the_generative_adapter_does_not_apply_veo_s_limits():
    """A backend that takes 12s clips and nine references should get them."""
    refs = [f"r{n}.png" for n in range(9)]
    spec = ShotSpec.from_intent(
        ShotIntent(shot_id="s1", description="d", duration_s=12), reference_images=refs
    )
    assert spec.duration_s == 12
    assert spec.reference_images == refs


def test_render_plan_holds_intents():
    plan = RenderPlan(intents=[ShotIntent(shot_id="s1", description="d")])
    assert plan.intents[0].shot_id == "s1"
    assert not hasattr(plan, "prompts")
