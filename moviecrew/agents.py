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


class PrompterAgent(Agent):
    role = "prompter"
    system_prompt = (
        "You are the Prompter. Given one shot, write a single Veo prompt describing only "
        "that shot's action, framing, and camera movement, plus a matching negative "
        "prompt. Never request on-screen text, captions, or subtitles.\n"
        'Respond with JSON only: {"prompts": [{"shot_id": str, "prompt": str, '
        '"negative_prompt": str}]}.'
    )

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
        "You are the Editor. Given every shot id, return the final render order.\n"
        'Respond with JSON only: {"order": [str, ...]}.'
    )

    def build_user(self, *, shot_ids: list[str]) -> str:
        return json.dumps({"shot_ids": shot_ids}, indent=2)
