"""Deterministic offline LLMClient for tests and dev without network/API keys.

Returns canned JSON per task. The IDs are chosen to line up across tasks
(scene "sc1" -> shots "sc1-sh1"/"sc1-sh2" -> prompts/flags keyed by those
shot ids) so a caller can drive the full schema — Bible, Scene, Shot,
VeoPrompt, ContinuityFlag, RenderPlan — end to end from mock responses
alone.
"""

from __future__ import annotations

from typing import Any

from .llm import LLMClient

_RESPONSES: dict[str, dict[str, Any]] = {
    "director": {
        "title": "The Last Lighthouse",
        "concept": "A keeper and a sea spirit strike a quiet bargain to outlast a storm.",
        "outline": ["Arrival at the lighthouse", "The bargain", "The storm breaks"],
    },
    "writer": {
        "scenes": [
            {
                "id": "sc1",
                "title": "Arrival at the lighthouse",
                "synopsis": "Mara climbs the cliff path as the storm gathers offshore.",
                "location_id": "loc1",
                "character_ids": ["ch1"],
            }
        ]
    },
    "designer": {
        "style": "muted watercolor realism",
        "palette": "slate blue, storm grey, lantern amber",
        "mood": "tense, melancholic, hopeful",
        "characters": [
            {
                "id": "ch1",
                "name": "Mara",
                "description": "weathered lighthouse keeper, oilskin coat, salt-grey hair",
                "reference_image_ids": ["ref-ch1-a"],
            }
        ],
        "locations": [
            {
                "id": "loc1",
                "name": "Cliffside Lighthouse",
                "description": "white stone tower on a black-rock cliff above a churning sea",
                "reference_image_ids": ["ref-loc1-a"],
            }
        ],
    },
    "cinematographer": {
        "shots": [
            {
                "id": "sc1-sh1",
                "scene_id": "sc1",
                "description": "Wide shot: Mara climbs the cliff path, waves crashing below.",
                "duration_s": 8,
                "camera": "slow dolly-in, low angle",
                "aspect_ratio": "16:9",
                "reference_image_ids": ["ref-loc1-a"],
            },
            {
                "id": "sc1-sh2",
                "scene_id": "sc1",
                "description": "Close-up: Mara's hand on the lighthouse door, rain streaking.",
                "duration_s": 4,
                "camera": "static close-up",
                "aspect_ratio": "16:9",
                "reference_image_ids": ["ref-ch1-a"],
            },
        ]
    },
    "prompter": {
        "prompts": [
            {
                "shot_id": "sc1-sh1",
                "prompt": (
                    "Wide shot of a weathered lighthouse keeper climbing a black-rock "
                    "cliff path toward a white stone lighthouse, storm waves crashing "
                    "below, muted watercolor realism, slate blue and storm grey palette, "
                    "slow dolly-in from a low angle."
                ),
                "negative_prompt": "blurry, distorted anatomy, modern clothing",
                "duration_s": 8,
                "aspect_ratio": "16:9",
                "reference_image_ids": ["ref-loc1-a"],
            },
            {
                "shot_id": "sc1-sh2",
                "prompt": (
                    "Close-up of a weathered hand pushing open a lighthouse door, "
                    "rain streaking down weathered wood, lantern amber light spilling "
                    "out, static composition."
                ),
                "negative_prompt": "blurry, distorted anatomy, modern clothing",
                "duration_s": 4,
                "aspect_ratio": "16:9",
                "reference_image_ids": ["ref-ch1-a"],
            },
        ]
    },
    "continuity": {
        "flags": [
            {
                "shot_id": "sc1-sh2",
                "severity": "info",
                "message": "Confirm Mara's coat color stays consistent with sc1-sh1.",
            }
        ]
    },
    "editor": {
        "prompt_order": ["sc1-sh1", "sc1-sh2"],
        "total_duration_s": 12,
    },
}


class MockLLMClient(LLMClient):
    """No-network, no-API-key LLMClient returning fixed, coherent JSON."""

    def complete_json(self, *, task: str, system: str, user: str) -> dict[str, Any]:
        try:
            return _RESPONSES[task]
        except KeyError as exc:
            raise ValueError(f"MockLLMClient has no canned response for task '{task}'") from exc
