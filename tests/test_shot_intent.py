"""Tests for `ShotIntent` and the adapters that turn one into a request.

The point of these is the boundary, not the dataclass. An intent must be able
to say things a given backend cannot do — a 12-second shot, five reference
images — and the adapter must be the only place those get cut down. If a
constraint leaks back into the intent, a shot can no longer be expressed
without first deciding what will render it, which is the exact problem
`ShotIntent` replaced `VeoPrompt` to solve.
"""

from __future__ import annotations

import pytest

from moviecrew.render import ShotSpec
from moviecrew.schema import (
    VEO_LEGAL_DURATIONS_S,
    VEO_MAX_REFERENCE_IMAGES,
    RenderPlan,
    ShotIntent,
)
from moviecrew.video import VeoPrompt, veo_prompt


# ---------------------------------------------------------------------- #
# The intent carries no backend's limits                                  #
# ---------------------------------------------------------------------- #


def test_duration_is_not_snapped_to_veo_lengths():
    """11.5s is not a legal Veo clip, and an intent may still ask for it."""
    intent = ShotIntent(shot_id="s1", description="a long walk", duration_s=11.5)
    assert intent.duration_s == 11.5
    assert intent.duration_s not in VEO_LEGAL_DURATIONS_S


def test_references_are_not_capped_at_veo_s_limit():
    refs = [f"ref{n}.png" for n in range(VEO_MAX_REFERENCE_IMAGES + 2)]
    intent = ShotIntent(shot_id="s1", description="d", reference_images=refs)
    assert len(intent.reference_images) == len(refs)


def test_an_aspect_ratio_veo_rejects_is_still_expressible():
    """2.39:1 anamorphic isn't a Veo ratio; the intent is not Veo's."""
    assert ShotIntent(shot_id="s1", description="d", aspect_ratio="239:100")


def test_a_malformed_aspect_ratio_is_still_refused():
    """Neutral does not mean unvalidated — the shape has to be a ratio."""
    with pytest.raises(ValueError, match="W:H"):
        ShotIntent(shot_id="s1", description="d", aspect_ratio="widescreen")


def test_a_nonpositive_duration_is_refused():
    with pytest.raises(ValueError, match="positive"):
        ShotIntent(shot_id="s1", description="d", duration_s=0)


def test_defaults_are_not_shared_between_intents():
    a = ShotIntent(shot_id="a", description="d")
    b = ShotIntent(shot_id="b", description="d")
    a.reference_images.append("x.png")
    assert b.reference_images == []


# ---------------------------------------------------------------------- #
# The Veo adapter is where Veo's limits apply                             #
# ---------------------------------------------------------------------- #


def test_adapter_snaps_the_duration():
    prompt = veo_prompt(ShotIntent(shot_id="s1", description="d", duration_s=11.5))
    assert prompt.duration_s in VEO_LEGAL_DURATIONS_S


def test_adapter_truncates_references_to_veo_s_cap():
    refs = [f"ref{n}.png" for n in range(VEO_MAX_REFERENCE_IMAGES + 2)]
    prompt = veo_prompt(ShotIntent(shot_id="s1", description="d", reference_images=refs))
    assert len(prompt.reference_images) == VEO_MAX_REFERENCE_IMAGES
    assert prompt.reference_images == refs[:VEO_MAX_REFERENCE_IMAGES]


def test_adapting_leaves_the_intent_intact():
    """What was asked for stays recoverable after a request that couldn't
    honour it — that is the whole reason the two are separate objects."""
    refs = [f"ref{n}.png" for n in range(VEO_MAX_REFERENCE_IMAGES + 2)]
    intent = ShotIntent(shot_id="s1", description="d", duration_s=11.5, reference_images=refs)

    veo_prompt(intent)

    assert intent.duration_s == 11.5
    assert len(intent.reference_images) == len(refs)


def test_adapter_carries_the_text_across():
    intent = ShotIntent(
        shot_id="sc1-sh1",
        description="Mara hauls herself onto the ledge.",
        negative="blurry, text",
    )
    prompt = veo_prompt(intent)
    assert prompt.shot_id == "sc1-sh1"
    assert prompt.prompt == "Mara hauls herself onto the ledge."
    assert prompt.negative_prompt == "blurry, text"


def test_adapter_refuses_a_ratio_veo_cannot_render():
    """The rejection lands at the boundary, where it is actionable — not at
    plan time, where it would have blocked writing the shot at all."""
    intent = ShotIntent(shot_id="s1", description="d", aspect_ratio="239:100")
    with pytest.raises(ValueError, match="aspect_ratio"):
        veo_prompt(intent)


def test_veo_prompt_is_not_importable_from_the_schema():
    """It is a vendor's shape and belongs at the vendor's boundary."""
    import moviecrew.schema as schema

    assert not hasattr(schema, "VeoPrompt")
    assert isinstance(veo_prompt(ShotIntent(shot_id="s", description="d")), VeoPrompt)


# ---------------------------------------------------------------------- #
# The generative adapter takes the same intent                            #
# ---------------------------------------------------------------------- #


def test_one_intent_feeds_both_adapters():
    """The same shot goes to Veo and to a generative backend unchanged — the
    thing a vendor-shaped centre made impossible."""
    intent = ShotIntent(
        shot_id="sc1-sh1",
        description="Mara hauls herself onto the ledge.",
        negative="blurry",
        duration_s=8,
        reference_images=["mara.png"],
    )

    veo = veo_prompt(intent)
    spec = ShotSpec.from_intent(intent)

    assert veo.prompt == spec.prompt == intent.description
    assert veo.negative_prompt == spec.negative_prompt == intent.negative
    assert veo.reference_images == spec.reference_images == ["mara.png"]


def test_the_generative_adapter_does_not_apply_veo_s_limits():
    """A backend that takes 12s clips should get 12 seconds, not 8."""
    spec = ShotSpec.from_intent(ShotIntent(shot_id="s1", description="d", duration_s=12))
    assert spec.duration_s == 12


# ---------------------------------------------------------------------- #
# The plan holds intents                                                  #
# ---------------------------------------------------------------------- #


def test_render_plan_holds_intents():
    plan = RenderPlan(intents=[ShotIntent(shot_id="s1", description="d")])
    assert plan.intents[0].shot_id == "s1"
    assert not hasattr(plan, "prompts")
