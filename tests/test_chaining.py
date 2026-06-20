"""Tests for deterministic continuity-chain planning, fully offline.

normalize_chains() takes the editor's raw (LLM-proposed) chain grouping and
makes it safe and Veo-legal: every shot lands in exactly one chain, unknown
ids are dropped, oversized chains are split, and the result is ordered by
each chain's first member's position in `order`.
"""

from moviecrew.crew import MovieCrew
from moviecrew.mock import MockLLMClient
from moviecrew.rules import normalize_chains
from moviecrew.schema import VEO_MAX_CHAIN_SEGMENTS, Shot


def _shot(shot_id: str) -> Shot:
    return Shot(id=shot_id, scene_id="sc1", description="x", duration_s=4)


def test_normalize_chains_keeps_a_valid_grouping():
    shots = [_shot("a"), _shot("b"), _shot("c")]
    order = ["a", "b", "c"]
    chains = normalize_chains(shots, order, [["a", "b"], ["c"]])
    assert chains == [["a", "b"], ["c"]]


def test_normalize_chains_sorts_members_by_order_index():
    shots = [_shot("a"), _shot("b")]
    order = ["a", "b"]
    chains = normalize_chains(shots, order, [["b", "a"]])
    assert chains == [["a", "b"]]


def test_normalize_chains_singletons_ungrouped_shots():
    shots = [_shot("a"), _shot("b"), _shot("c")]
    order = ["a", "b", "c"]
    chains = normalize_chains(shots, order, [["a"]])
    assert chains == [["a"], ["b"], ["c"]]


def test_normalize_chains_drops_unknown_ids():
    shots = [_shot("a"), _shot("b")]
    order = ["a", "b"]
    chains = normalize_chains(shots, order, [["a", "ghost", "b"]])
    assert chains == [["a", "b"]]


def test_normalize_chains_drops_duplicate_assignment_across_raw_chains():
    shots = [_shot("a"), _shot("b")]
    order = ["a", "b"]
    chains = normalize_chains(shots, order, [["a", "b"], ["a"]])
    assert chains == [["a", "b"]]


def test_normalize_chains_splits_oversized_chains():
    shot_ids = [f"s{i}" for i in range(VEO_MAX_CHAIN_SEGMENTS + 5)]
    shots = [_shot(shot_id) for shot_id in shot_ids]
    chains = normalize_chains(shots, shot_ids, [shot_ids])

    assert len(chains) == 2
    assert chains[0] == shot_ids[:VEO_MAX_CHAIN_SEGMENTS]
    assert chains[1] == shot_ids[VEO_MAX_CHAIN_SEGMENTS:]
    for chain in chains:
        assert len(chain) <= VEO_MAX_CHAIN_SEGMENTS


def test_normalize_chains_orders_chains_by_first_member_index():
    shots = [_shot("a"), _shot("b"), _shot("c")]
    order = ["a", "b", "c"]
    chains = normalize_chains(shots, order, [["c"], ["a", "b"]])
    assert chains == [["a", "b"], ["c"]]


def test_make_produces_well_formed_chains_via_mock():
    project = MovieCrew(MockLLMClient()).make("A keeper and a sea spirit outlast a storm.")
    render_plan = project.render_plan
    assert render_plan is not None

    all_shot_ids = {shot.id for scene in project.scenes for shot in scene.shots}
    chained_ids = [shot_id for chain in render_plan.chains for shot_id in chain]

    assert set(chained_ids) == all_shot_ids
    assert len(chained_ids) == len(set(chained_ids))  # every shot exactly once
    for chain in render_plan.chains:
        assert len(chain) <= VEO_MAX_CHAIN_SEGMENTS
