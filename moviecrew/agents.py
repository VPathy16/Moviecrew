"""Agent layer: one focused LLM call per pipeline role.

Each agent pairs a fixed system prompt (what JSON shape to return, matching
moviecrew.schema exactly) with a `build_user` method that serializes its
inputs into the user message. Agents only talk to LLMClient.complete_json;
ordering, deduplication, and deterministic rules live in moviecrew.crew /
moviecrew.rules.
"""

from __future__ import annotations

import json
from typing import Any

from .llm import LLMClient


class Agent:
    """Base agent: fixed role/system prompt, JSON in, dict out."""

    role: str = ""
    system_prompt: str = ""

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def build_user(self, **kwargs: Any) -> str:
        return json.dumps(kwargs, indent=2)

    def run(self, **kwargs: Any) -> dict[str, Any]:
        user = self.build_user(**kwargs)
        return self.llm.complete_json(task=self.role, system=self.system_prompt, user=user)


class DirectorAgent(Agent):
    role = "director"
    system_prompt = (
        "You are the Director. Given a one-line movie concept, invent a title, a "
        "one-sentence logline, and a short beat outline.\n"
        'Respond with JSON only: {"title": str, "logline": str, "outline": [str, ...]}.'
    )

    def build_user(self, *, concept: str) -> str:
        return json.dumps({"concept": concept}, indent=2)


class WriterAgent(Agent):
    role = "writer"
    system_prompt = (
        "You are the Writer. Given the title, logline, and outline, break the story into "
        "scenes.\n"
        'Respond with JSON only: {"scenes": [{"id": str, "slug": str, "title": str, '
        '"summary": str, "location_id": str, "character_ids": [str, ...]}]}.'
    )

    def build_user(self, *, title: str, logline: str, outline: list[str]) -> str:
        return json.dumps({"title": title, "logline": logline, "outline": outline}, indent=2)


class DesignerAgent(Agent):
    role = "designer"
    system_prompt = (
        "You are the Production Designer. Given the title, logline, and scenes, define the "
        "visual Bible: overall style, color palette, mood, and every character and location "
        "referenced by the scenes.\n"
        'Respond with JSON only: {"style": str, "palette": str, "mood": str, '
        '"characters": [{"id": str, "name": str, "description": str, '
        '"reference_images": [str, ...]}], "locations": [{"id": str, "name": str, '
        '"description": str, "reference_images": [str, ...]}]}.'
    )

    def build_user(self, *, title: str, logline: str, scenes: list[dict[str, Any]]) -> str:
        return json.dumps({"title": title, "logline": logline, "scenes": scenes}, indent=2)


class CinematographerAgent(Agent):
    role = "cinematographer"
    system_prompt = (
        "You are the Cinematographer. Given one scene, break it into shots. Every shot's "
        "duration_s MUST be 4, 6, or 8 seconds.\n"
        'Respond with JSON only: {"shots": [{"id": str, "scene_id": str, '
        '"description": str, "duration_s": int, "camera_move": str, "lens": str, '
        '"framing": str}]}.'
    )

    def build_user(self, *, scene: dict[str, Any]) -> str:
        return json.dumps({"scene": scene}, indent=2)


DETAIL_LEVELS: dict[str, dict[str, Any]] = {
    "lean": {"words": "30-45", "layered": False},
    "cinematic": {"words": "65-85", "layered": True},
    "maximal": {"words": "100-130", "layered": True},
}

_PROMPTER_LEAD_RULE = (
    "Veo animates verbs, not adjectives. OPEN every prompt with one continuous physical "
    "action that has a beginning and end — concrete micro-movements for the subject AND "
    "the environment. Never a static state like 'stands looking concerned'; write what "
    "the body does. A 4s shot is one beat; an 8s shot is a short arc of 2-3 linked "
    "movements. Put camera move, lens, lighting and style AFTER the action, never before "
    "it. Never request readable on-screen text — convey it through imagery."
)

_PROMPTER_LAYERS = (
    "1 ACTION (granular, subject + environment)",
    "2 SUBJECT specifics (wardrobe, materials, build, what hands/face do)",
    "3 CAMERA as motion (speed + path, not just the move name)",
    "4 LIGHT (source, direction, colour, hardness, effect on surfaces)",
    "5 LENS & DEPTH (focal length + depth behaviour)",
    "6 ATMOSPHERE & TEXTURE (haze, grain, grime)",
    "7 SOUND (Veo audio — name it)",
)


def _build_prompter_system_prompt(detail: str) -> str:
    level = DETAIL_LEVELS[detail]
    lines = [
        "You are the Prompter. Given one shot, write a single dense Veo prompt plus a "
        "matching negative prompt.",
        "",
        _PROMPTER_LEAD_RULE,
        "",
    ]
    if level["layered"]:
        lines.append("Weave in all seven layers, roughly in this flow:")
        lines.extend(_PROMPTER_LAYERS)
    else:
        lines.append("Keep it tight: action, then camera, then light — nothing else.")
    lines.append("")
    lines.append(
        f"Target {level['words']} words. If the shot is a consistency anchor "
        "(consistency_anchor is true), keep weaving the character's physical descriptor "
        "(build, wardrobe, distinguishing features) into the subject so the prompt "
        "matches its reference image, as today."
    )
    lines.append(
        'Respond with JSON only: {"prompts": [{"shot_id": str, "prompt": str, '
        '"negative_prompt": str}]}.'
    )
    return "\n".join(lines)


class PrompterAgent(Agent):
    """Writes the Veo prompt for one shot, at an injectable detail level.

    `detail` picks a word-count target and whether the system prompt demands
    the full seven-layer flow (action/subject/camera/light/lens/atmosphere/
    sound) or stays to a lean action+camera+light sketch — see DETAIL_LEVELS.
    """

    role = "prompter"

    def __init__(self, llm: LLMClient, detail: str = "cinematic") -> None:
        super().__init__(llm)
        if detail not in DETAIL_LEVELS:
            raise ValueError(
                f"unknown prompt detail level: {detail!r} (must be one of "
                f"{sorted(DETAIL_LEVELS)})"
            )
        self.detail = detail
        self.system_prompt = _build_prompter_system_prompt(detail)

    def build_user(self, *, shot: dict[str, Any]) -> str:
        return json.dumps({"shot": shot}, indent=2)


class ContinuityAgent(Agent):
    role = "continuity"
    system_prompt = (
        "You are Continuity. Given every scene/shot and every Veo prompt, flag anything "
        "inconsistent: appearance drift, mismatched locations, repeated mistakes.\n"
        'Respond with JSON only: {"flags": [{"target": str, "kind": '
        '"info"|"warning"|"error", "message": str}]}.'
    )

    def build_user(self, *, scenes: list[dict[str, Any]], prompts: list[dict[str, Any]]) -> str:
        return json.dumps({"scenes": scenes, "prompts": prompts}, indent=2)


class EditorAgent(Agent):
    role = "editor"
    system_prompt = (
        "You are the Editor. Given every shot id, return the final render order, "
        "plus how shots chain into continuous takes for Veo's extend-from-final-frame "
        "feature. Group ADJACENT shots that form one continuous take into a chain "
        "(shot ids in extend order); a hard cut starts a new chain; a standalone shot "
        "is a one-element chain. Every shot id must appear exactly once across all "
        "chains, consistent with order.\n"
        'Respond with JSON only: {"order": [str, ...], "chains": [[str, ...], ...]}.'
    )

    def build_user(self, *, shot_ids: list[str]) -> str:
        return json.dumps({"shot_ids": shot_ids}, indent=2)
