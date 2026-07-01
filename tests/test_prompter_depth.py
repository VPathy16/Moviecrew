"""Tests for prompter detail levels and motion-first prompt construction, fully offline."""

from __future__ import annotations

import re

import pytest

from moviecrew.agents import DETAIL_LEVELS, PrompterAgent
from moviecrew.crew import MovieCrew
from moviecrew.mock import MockLLMClient

_ACTION_VERBS = {
    "grips",
    "grip",
    "hauls",
    "haul",
    "presses",
    "press",
    "shoves",
    "shove",
    "climbs",
    "climb",
    "pushes",
    "push",
    "drags",
    "drag",
    "leans",
    "lean",
    "reaches",
    "reach",
    "braces",
    "brace",
    "scans",
    "scan",
}


def _first_words(text: str, n: int = 10) -> list[str]:
    return re.findall(r"[A-Za-z']+", text.lower())[:n]


@pytest.fixture
def mock_prompts() -> list[dict]:
    return MockLLMClient().complete_json(task="prompter", system="", user="")["prompts"]


def test_mock_prompts_open_with_an_action_verb(mock_prompts):
    for prompt in mock_prompts:
        words = set(_first_words(prompt["prompt"]))
        assert words & _ACTION_VERBS, prompt["prompt"]


def test_mock_prompts_are_cinematic_depth(mock_prompts):
    for prompt in mock_prompts:
        text = prompt["prompt"].lower()
        assert any(word in text for word in ("light", "lantern", "glow", "haze")), text
        assert re.search(r"\d+mm", text), text


def test_mock_prompts_carry_a_sound_cue(mock_prompts):
    sound_words = ("roars", "crash", "creaks", "groan", "patters", "gusts")
    for prompt in mock_prompts:
        text = prompt["prompt"].lower()
        assert any(word in text for word in sound_words), text


def test_lean_system_prompt_is_short_and_unlayered():
    agent = PrompterAgent(MockLLMClient(), detail="lean")
    assert DETAIL_LEVELS["lean"]["words"] in agent.system_prompt
    assert "ACTION" not in agent.system_prompt
    assert "SOUND" not in agent.system_prompt


def test_cinematic_system_prompt_requires_all_seven_layers():
    agent = PrompterAgent(MockLLMClient())
    assert agent.detail == "cinematic"
    for layer in ("ACTION", "SUBJECT", "CAMERA", "LIGHT", "LENS", "ATMOSPHERE", "SOUND"):
        assert layer in agent.system_prompt
    assert DETAIL_LEVELS["cinematic"]["words"] in agent.system_prompt


def test_maximal_system_prompt_targets_a_higher_word_count():
    agent = PrompterAgent(MockLLMClient(), detail="maximal")
    assert DETAIL_LEVELS["maximal"]["words"] in agent.system_prompt
    for layer in ("ACTION", "SUBJECT", "CAMERA", "LIGHT", "LENS", "ATMOSPHERE", "SOUND"):
        assert layer in agent.system_prompt


def test_unknown_detail_level_raises():
    with pytest.raises(ValueError):
        PrompterAgent(MockLLMClient(), detail="extra-spicy")


def test_prompt_detail_flows_through_movie_crew_without_breaking_shape():
    project = MovieCrew(MockLLMClient(), prompt_detail="lean").make(
        "A keeper and a sea spirit outlast a storm."
    )

    assert project.render_plan is not None
    for prompt in project.render_plan.prompts:
        assert prompt.prompt
        assert prompt.negative_prompt
        assert prompt.aspect_ratio == "16:9"
