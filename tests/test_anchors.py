"""Tests for select_anchors (cross-cut consistency anchoring), fully offline."""

from __future__ import annotations

from moviecrew.crew import MovieCrew
from moviecrew.mock import MockLLMClient
from moviecrew.production import resolve_shot
from moviecrew.rules import select_anchors
from moviecrew.schema import Bible, Character, Scene, Shot


def _shot(shot_id: str, scene_id: str, *, duration_s: int = 4) -> Shot:
    return Shot(id=shot_id, scene_id=scene_id, description="x", duration_s=duration_s)


def _scene(scene_id: str, *, character_ids: list[str], shots: list[Shot]) -> Scene:
    return Scene(
        id=scene_id,
        slug=scene_id,
        title=scene_id,
        summary="x",
        character_ids=character_ids,
        shots=shots,
    )


def _bible(characters: list[Character]) -> Bible:
    return Bible(style="s", palette="p", mood="m", characters=characters)


_ALWAYS_REAL = lambda path: True  # noqa: E731
_NEVER_REAL = lambda path: False  # noqa: E731


def test_chain_head_with_real_ref_is_anchored():
    sh1, sh2 = _shot("sc1-sh1", "sc1", duration_s=4), _shot("sc1-sh2", "sc1", duration_s=4)
    scene = _scene("sc1", character_ids=["ch1"], shots=[sh1, sh2])
    ch1 = Character(id="ch1", name="ch1", description="x", reference_images=["ref-ch1.png"])

    select_anchors([scene], [["sc1-sh1", "sc1-sh2"]], _bible([ch1]), is_real=_ALWAYS_REAL)

    assert sh1.consistency_anchor is True
    assert sh1.reference_image_ids == ["ref-ch1.png"]


def test_anchoring_does_not_rewrite_the_shot_s_duration():
    """Veo needs 8s clips when references are present. That is Veo's rule and
    VeoBackend applies it; anchoring must not rewrite the intended cut."""
    sh1 = _shot("sc1-sh1", "sc1", duration_s=4)
    scene = _scene("sc1", character_ids=["ch1"], shots=[sh1])
    ch1 = Character(id="ch1", name="ch1", description="x", reference_images=["ref-ch1.png"])

    select_anchors([scene], [["sc1-sh1"]], _bible([ch1]), is_real=_ALWAYS_REAL)

    assert sh1.duration_s == 4


def test_anchoring_does_not_truncate_references_to_a_backend_s_cap():
    refs = [f"ref{n}.png" for n in range(5)]
    sh1 = _shot("sc1-sh1", "sc1", duration_s=4)
    scene = _scene("sc1", character_ids=["ch1"], shots=[sh1])
    ch1 = Character(id="ch1", name="ch1", description="x", reference_images=refs)

    select_anchors([scene], [["sc1-sh1"]], _bible([ch1]), is_real=_ALWAYS_REAL)

    assert sh1.reference_image_ids == refs


def test_non_head_shots_in_a_chain_stay_unanchored():
    sh1, sh2 = _shot("sc1-sh1", "sc1"), _shot("sc1-sh2", "sc1")
    scene = _scene("sc1", character_ids=["ch1"], shots=[sh1, sh2])
    ch1 = Character(id="ch1", name="ch1", description="x", reference_images=["ref-ch1.png"])

    select_anchors([scene], [["sc1-sh1", "sc1-sh2"]], _bible([ch1]), is_real=_ALWAYS_REAL)

    assert sh2.consistency_anchor is False
    assert sh2.reference_image_ids == []


def test_charless_chain_stays_unanchored():
    sh1 = _shot("sc1-sh1", "sc1")
    scene = _scene("sc1", character_ids=[], shots=[sh1])

    select_anchors([scene], [["sc1-sh1"]], _bible([]), is_real=_ALWAYS_REAL)

    assert sh1.consistency_anchor is False
    assert sh1.reference_image_ids == []


def test_head_whose_characters_lack_a_real_ref_stays_unanchored():
    sh1 = _shot("sc1-sh1", "sc1")
    scene = _scene("sc1", character_ids=["ch1"], shots=[sh1])
    ch1 = Character(id="ch1", name="ch1", description="x", reference_images=["ref-ch1.png"])

    select_anchors([scene], [["sc1-sh1"]], _bible([ch1]), is_real=_NEVER_REAL)

    assert sh1.consistency_anchor is False
    assert sh1.reference_image_ids == []


def test_select_anchors_overwrites_stale_anchor_state():
    sh1 = _shot("sc1-sh1", "sc1")
    sh1.consistency_anchor = True
    sh1.reference_image_ids = ["stale.png"]
    scene = _scene("sc1", character_ids=[], shots=[sh1])

    select_anchors([scene], [["sc1-sh1"]], _bible([]), is_real=_ALWAYS_REAL)

    assert sh1.consistency_anchor is False
    assert sh1.reference_image_ids == []


class _FakeStillProvider:
    """Produces a still for exactly one character id, for end-to-end tests."""

    def __init__(self, character_id: str) -> None:
        self.character_id = character_id

    def generate(self, character):
        if character.id == self.character_id:
            return b"fake-png-bytes"
        return None


def test_end_to_end_anchoring_via_mock_pipeline(tmp_path):
    out_dir = str(tmp_path / "stills")
    crew = MovieCrew(
        MockLLMClient(),
        reference_provider=_FakeStillProvider("ch1"),
        reference_out_dir=out_dir,
    )

    project = crew.make("A keeper and a sea spirit outlast a storm.")
    render_plan = project.render_plan
    assert render_plan is not None

    first_chain = render_plan.chains[0]
    head_id = first_chain[0]
    head = next(
        shot for scene in project.scenes for shot in scene.shots if shot.id == head_id
    )

    assert head.consistency_anchor is True
    assert head.reference_image_ids
    assert all(path.startswith(out_dir) for path in head.reference_image_ids)

    # The intent carries no copy of the references — they are resolved from
    # the shot at execution time, so approving a board later is reflected.
    head_intent = next(i for i in render_plan.intents if i.shot_id == head_id)
    assert not hasattr(head_intent, "reference_images")
    assert head_intent.duration_s == head.duration_s

    state = resolve_shot(project, head_id)
    assert state.reference_images == head.reference_image_ids

    expected_duration = sum(
        shot.duration_s for scene in project.scenes for shot in scene.shots
    )
    assert render_plan.est_duration_s == expected_duration
