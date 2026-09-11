"""Tests for deterministic continuity-chain planning, fully offline.

normalize_chains() takes the editor's raw (LLM-proposed) chain grouping and
makes it safe and Veo-legal: every shot lands in exactly one chain, unknown
ids are dropped, oversized chains are split, and the result is ordered by
each chain's first member's position in `order`.
"""

from moviecrew.crew import MovieCrew
from moviecrew.mock import MockLLMClient
from moviecrew.rules import normalize_chains
from moviecrew.schema import Shot
from moviecrew.video import VEO_MAX_CHAIN_SEGMENTS, segment_for_veo


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


def test_normalize_chains_drops_duplicate_within_a_single_raw_chain():
    shots = [_shot("a"), _shot("b")]
    order = ["a", "b"]
    chains = normalize_chains(shots, order, [["a", "a", "b"]])
    assert chains == [["a", "b"]]


def test_a_long_editorial_chain_stays_whole():
    """A chain is a creative statement — these shots are one continuous take.
    Veo can only execute 21 segments per extend-run, but that is Veo's
    problem and `video.segment_for_veo` solves it at the boundary. Cutting
    the canonical chain here would make an editorial decision on behalf of
    whichever backend happened to be configured."""
    shot_ids = [f"s{i}" for i in range(VEO_MAX_CHAIN_SEGMENTS + 5)]
    shots = [_shot(shot_id) for shot_id in shot_ids]

    chains = normalize_chains(shots, shot_ids, [shot_ids])

    assert chains == [shot_ids]
    assert len(chains[0]) > VEO_MAX_CHAIN_SEGMENTS


def test_the_veo_adapter_segments_that_long_chain_for_execution():
    shot_ids = [f"s{i}" for i in range(VEO_MAX_CHAIN_SEGMENTS + 5)]
    shots = [_shot(shot_id) for shot_id in shot_ids]
    chain = normalize_chains(shots, shot_ids, [shot_ids])[0]

    runs = segment_for_veo(chain)

    assert len(runs) == 2
    assert [shot_id for run in runs for shot_id in run] == chain
    for run in runs:
        assert len(run) <= VEO_MAX_CHAIN_SEGMENTS


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
        for run in segment_for_veo(chain):
            assert len(run) <= VEO_MAX_CHAIN_SEGMENTS
