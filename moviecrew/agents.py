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
        "scenes. Give each scene an event, goal, obstacle, turning_point, and acting_tasks "
        "(a dictionary from character ID to observable tactic, including what the eyes attend to). "
        "Every scene must change the situation; do not repeat the same action in successive scenes.\n"
        'Respond with JSON only: {"scenes": [{"id": str, "slug": str, "title": str, '
        '"summary": str, "location_id": str, "character_ids": [str, ...], '
        '"event": str, "goal": str, "obstacle": str, "turning_point": str, "acting_tasks": {str: str}}]}.'
    )

    _ASSETS_FIRST_ADDENDUM = (
        "Write the story FOR this cast and world. Use these characters/props/locations "
        "by id; do not invent replacements for existing roles."
    )

    def build_user(
        self,
        *,
        title: str,
        logline: str,
        outline: list[str],
        provided_bible: Any = None,
    ) -> str:
        data: dict[str, Any] = {"title": title, "logline": logline, "outline": outline}
        if provided_bible is not None:
            data["provided_bible"] = (
                provided_bible.to_dict()
                if hasattr(provided_bible, "to_dict")
                else provided_bible
            )
        return json.dumps(data, indent=2)

    def run(  # type: ignore[override]
        self,
        *,
        title: str,
        logline: str,
        outline: list[str],
        provided_bible: Any = None,
    ) -> dict[str, Any]:
        user = self.build_user(
            title=title, logline=logline, outline=outline, provided_bible=provided_bible
        )
        system = self.system_prompt
        if provided_bible is not None:
            system = f"{self.system_prompt}\n\n{self._ASSETS_FIRST_ADDENDUM}"
        return self.llm.complete_json(task=self.role, system=system, user=user)


class DesignerAgent(Agent):
    role = "designer"
    system_prompt = (
        "You are the Production Designer. Given the title, logline, and scenes, define the "
        "visual Bible: overall style, color palette, mood, and every character, prop and "
        "location referenced by the scenes.\n"
        'Respond with JSON only: {"style": str, "palette": str, "mood": str, '
        '"characters": [{"id": str, "name": str, "description": str, '
        '"reference_images": [str, ...]}], "locations": [{"id": str, "name": str, '
        '"description": str, "reference_images": [str, ...]}], '
        '"props": [{"id": str, "name": str, "description": str, '
        '"reference_images": [str, ...]}]}.'
    )

    _GAP_FILL_SYSTEM_PROMPT = (
        "You are the Production Designer. A visual Bible has already been provided. "
        "You may only FILL GAPS the story requires (e.g. a location the library lacks), "
        "appending new assets. Return all provided characters, props and locations "
        "byte-identical — their ids, descriptions and reference_images must be unchanged. "
        "Do not invent replacements for existing roles.\n"
        'Respond with JSON only: {"style": str, "palette": str, "mood": str, '
        '"characters": [...], "locations": [...], '
        '"props": [{"id": str, "name": str, "description": str, '
        '"reference_images": [str, ...]}]}.'
    )

    def build_user(
        self,
        *,
        title: str,
        logline: str,
        scenes: list[dict[str, Any]],
        provided_bible: Any = None,
    ) -> str:
        data: dict[str, Any] = {"title": title, "logline": logline, "scenes": scenes}
        if provided_bible is not None:
            data["provided_bible"] = (
                provided_bible.to_dict()
                if hasattr(provided_bible, "to_dict")
                else provided_bible
            )
        return json.dumps(data, indent=2)

    def run(  # type: ignore[override]
        self,
        *,
        title: str,
        logline: str,
        scenes: list[dict[str, Any]],
        provided_bible: Any = None,
    ) -> dict[str, Any]:
        user = self.build_user(
            title=title, logline=logline, scenes=scenes, provided_bible=provided_bible
        )
        system = self._GAP_FILL_SYSTEM_PROMPT if provided_bible is not None else self.system_prompt
        system += (
            '\nAlso return a top-level "sheet_notes" object keyed by "characters:<id>". '
            'For EVERY character, including provided characters, supply these exact keys: '
            'Appearance, Personality, Wardrobe, Expressions & poses, Voice & language, Continuity notes. '
            'Write concise production-ready details grounded in the story and provided identity. '
            'Preserve species, established appearance, references, language and wardrobe. '
            'Do not invent injuries, accessories or costumes unrelated to the story. '
            'Use "Not specified" where the story gives no basis. These are separate reviewable '
            'design notes; do not alter provided assets.'
        )
        return self.llm.complete_json(task=self.role, system=system, user=user)


class CinematographerAgent(Agent):
    role = "cinematographer"
    system_prompt = (
        "You are the Cinematographer. Given one scene, break it into shots. Give each "
        "shot the duration the cut actually wants, in seconds — 2.5, 5, 11.5 and 18 "
        "are all legitimate; do not round to fit any particular renderer, which will "
        "clamp or split later if it must. Durations must be positive. "
        "For every shot provide visible_character_ids and visible_prop_ids containing only IDs actually visible in this framing (empty arrays for none). Also provide image_prompt describing ONE opening still frame, its composition, visible subjects, lighting and lens; exclude movement over time, dialogue and sound. "
        "Plan cause and consequence. Each shot has story_contract_version=1, purpose, action "
        "(what the shot is about), entry_state and exit_state (non-empty dictionaries of stable "
        "entity/property keys to concise state labels), screen_direction, audio_intent and "
        "transition (cut, continuous, ellipsis). "
        "A shot is not one atomic action — it is one continuous piece of coverage. Put its "
        "temporal detail in optional beats: [{start_s, end_s, action}] covering the shot's own "
        "duration_s (a 4s shot is typically one beat; an 8-10s shot is often 2-4 linked beats). "
        "An expression change, an eyeline shift, a small movement, a focus rack, the camera "
        "starting or changing speed — these are beats inside the current shot, never by "
        "themselves a reason to start a new one. "
        "Every shot after a scene's first must set cut_reason: the concrete editorial reason "
        "this is a NEW shot rather than another beat of the last one — e.g. reveal new "
        "information, change POV, reaction, geography change, time compression, power shift, "
        "insert, transition. If you cannot name one, it is not a new shot — fold it into the "
        "previous shot's beats instead. The first shot of a scene has no cut_reason. "
        "If the scene carries target_duration_s, that is a budget: sum(shot.duration_s) for "
        "this scene should land close to it. Reaching it should come from fewer, longer, "
        "multi-beat shots, not from omitting story detail — the detail belongs in beats. If "
        "the scene carries over_budget_notice, a prior attempt at this same scene blew well "
        "past budget; read it and correct by merging shots, not by trimming actions out of the "
        "story. "
        "Use identical labels when a state is unchanged. Adjacent shots in a scene must agree on shared "
        "exit/entry keys unless an explicit ellipsis advances time. A cut changes framing, not physical "
        "facts. Vary shot size with a story reason; carry prop ownership and physical condition.\n"
        'Respond with JSON only: {"shots": [{"id": str, "scene_id": str, '
        '"description": str, "image_prompt": str, "visible_character_ids": [str], "visible_prop_ids": [str], "duration_s": number, "camera_move": str, "lens": str, '
        '"framing": str, "story_contract_version": 1, "purpose": str, "action": str, '
        '"entry_state": {str: str}, "exit_state": {str: str}, "screen_direction": str, '
        '"audio_intent": str, "transition": "cut"|"continuous"|"ellipsis", '
        '"beats": [{"start_s": number, "end_s": number, "action": str}], "cut_reason": str}]}.'
    )

    def build_user(self, *, scene: dict[str, Any]) -> str:
        return json.dumps({"scene": scene}, indent=2)


DETAIL_LEVELS: dict[str, dict[str, Any]] = {
    "lean": {"words": "30-45", "layered": False},
    "cinematic": {"words": "65-85", "layered": True},
    "maximal": {"words": "100-130", "layered": True},
}

_PROMPTER_LEAD_RULE = (
    "Video models animate verbs, not adjectives. OPEN every prompt with one continuous physical "
    "action that has a beginning and end — concrete micro-movements for the subject AND "
    "the environment. Never a static state like 'stands looking concerned'; write what "
    "the body does. If the shot supplies beats (its own timed sub-actions), narrate them in "
    "order as the linked arc of this one shot — do not collapse them into a single moment or "
    "treat any of them as needing their own shot; that decision was already made upstream. "
    "Without supplied beats, use duration as a rough guide: a 4s shot is one beat, an 8s shot "
    "a short arc of 2-3 linked movements. Put camera move, lens, lighting and style AFTER the "
    "action, never before it. Include readable in-scene text only when the shot explicitly "
    "requires it; preserve requested wording instead of substituting invented text. Otherwise "
    "avoid unrequested lettering. Rendering accuracy depends on the selected model and must be "
    "reviewed."
)

_PROMPTER_LAYERS = (
    "1 ACTION (granular, subject + environment)",
    "2 SUBJECT specifics (wardrobe, materials, build, what hands/face do)",
    "3 CAMERA as motion (speed + path, not just the move name)",
    "4 LIGHT (source, direction, colour, hardness, effect on surfaces)",
    "5 LENS & DEPTH (focal length + depth behaviour)",
    "6 ATMOSPHERE & TEXTURE (haze, grain, grime)",
    "7 SOUND (native audio — name it)",
)


def _build_prompter_system_prompt(detail: str) -> str:
    level = DETAIL_LEVELS[detail]
    lines = [
        "You are the Prompter. Given one shot, write a single dense shot prompt plus a "
        "matching negative prompt.",
        "",
        _PROMPTER_LEAD_RULE,
        "When context is supplied, use the current shot action and entry/exit states as authoritative. "
        "Use neighbouring shots only to ensure progression: never animate their actions in this shot. "
        "Write a self-contained instruction, not 'same as previous'. A hard cut may change composition; "
        "continuous action preserves motion direction. Preserve supplied character and world descriptors. "
        "Distinguish identity references from composition references. Never invent attached images. "
        "Integrate scene acting tasks through visible behaviour, feasible timing and sound. "
        "The intended ending state must follow the current action. Prefer concrete positive descriptions.",
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
    """Writes the shot prompt for one shot, at an injectable detail level.

    What it writes is the `description` of a `ShotIntent` — backend-neutral
    prose. Whichever backend renders the shot adapts that text itself.

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

    def build_user(self, *, shot: dict[str, Any], context: dict | None = None) -> str:
        data = {"shot": shot}
        if context is not None:
            data['context'] = context
        return json.dumps(data, indent=2)


class ContinuityAgent(Agent):
    role = "continuity"
    system_prompt = (
        "You are Continuity. Given every scene/shot and every shot prompt, flag anything "
        "inconsistent: appearance drift, mismatched locations, repeated mistakes.\n"
        'Respond with JSON only: {"flags": [{"target": str, "kind": '
        '"info"|"warning"|"error", "message": str}]}.'
    )

    def build_user(self, *, scenes: list[dict[str, Any]], prompts: list[dict[str, Any]]) -> str:
        return json.dumps({"scenes": scenes, "prompts": prompts}, indent=2)


class EditorAgent(Agent):
    role = "editor"
    system_prompt = (
        "You are the Editor. Given story intent, scenes and full shot states, return the final screening order. "
        "Preserve causal progression and flag coverage gaps in editorial_notes keyed by shot ID. "
        "Explain each cut using action, movement or sound. Never reorder an effect before its cause. "
        "Also return "
        "how shots group into continuous takes. A chain is an editorial "
        "statement: these shots play as one unbroken take, with no cut between them. "
        "Group ADJACENT shots that form one continuous take into a chain (in playing "
        "order); a hard cut starts a new chain; a standalone shot is a one-element "
        "chain. Chain length is a creative choice — do not shorten a take because you "
        "imagine a tool might struggle with it. Every shot id must appear exactly "
        "once across all chains, consistent with order.\n"
        'Respond with JSON only: {"order": [str, ...], "chains": [[str, ...], ...], '
        '"editorial_notes": {str: str}}.'
    )

    def build_user(self, *, shot_ids: list[str], context: dict | None = None) -> str:
        data = {"shot_ids": shot_ids}
        if context is not None:
            data['context'] = context
        return json.dumps(data, indent=2)
