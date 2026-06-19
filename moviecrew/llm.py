"""Model-agnostic LLM abstraction.

`LLMClient` is the single interface the (future) agent pipeline talks to.
`AnthropicLLMClient` implements it against the Claude API, importing the
`anthropic` package lazily so this module — and anything that only needs
the ABC or the mock client — imports fine even when the SDK isn't
installed.
"""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from typing import Any

# Per-task model routing. Heavier reasoning tasks (director, continuity)
# get the strongest model; mechanical tasks (editor) get the cheapest.
TASK_MODEL_ROUTING: dict[str, str] = {
    "director": "claude-opus-4-8",
    "continuity": "claude-opus-4-8",
    "writer": "claude-sonnet-4-6",
    "designer": "claude-sonnet-4-6",
    "cinematographer": "claude-sonnet-4-6",
    "prompter": "claude-sonnet-4-6",
    "editor": "claude-haiku-4-5-20251001",
}

DEFAULT_MODEL = "claude-sonnet-4-6"

_JSON_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def model_for_task(task: str) -> str:
    return TASK_MODEL_ROUTING.get(task, DEFAULT_MODEL)


def parse_json_response(text: str) -> dict[str, Any]:
    """Tolerantly parse a JSON object out of an LLM response.

    Strips ```json ... ``` fences (and bare ``` fences) and surrounding
    whitespace before falling back to a raw `json.loads`.
    """
    cleaned = _JSON_FENCE_RE.sub("", text.strip()).strip()
    return json.loads(cleaned)


class LLMClient(ABC):
    """Abstract LLM client used by every agent in the pipeline."""

    @abstractmethod
    def complete_json(self, *, task: str, system: str, user: str) -> dict[str, Any]:
        """Run a completion for `task` and return a parsed JSON object."""
        raise NotImplementedError


class AnthropicLLMClient(LLMClient):
    """LLMClient backed by the Anthropic Claude API.

    The `anthropic` package is imported lazily inside `__init__` so that
    importing this module never requires the SDK to be installed.
    """

    def __init__(self, api_key: str | None = None, *, max_tokens: int = 4096) -> None:
        import anthropic  # lazy import: optional dependency

        self._client = anthropic.Anthropic(api_key=api_key)
        self._max_tokens = max_tokens

    def complete_json(self, *, task: str, system: str, user: str) -> dict[str, Any]:
        model = model_for_task(task)
        response = self._client.messages.create(
            model=model,
            max_tokens=self._max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(
            block.text for block in response.content if getattr(block, "type", None) == "text"
        )
        return parse_json_response(text)
