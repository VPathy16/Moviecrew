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

# How much context to keep on each side of a decode failure. Enough to show
# the actual shape of the break (a dropped comma, an unterminated string)
# without echoing an entire response into a log or an error banner.
_EXCERPT_RADIUS = 120


def model_for_task(task: str) -> str:
    return TASK_MODEL_ROUTING.get(task, DEFAULT_MODEL)


class JSONParseError(ValueError):
    """A response could not be reduced to exactly one JSON object.

    The common base `OpenRouterLLMClient.complete_json` catches to decide
    whether a parse failure is worth one corrective retry. Never carries the
    full response text — only a bounded excerpt — so a caller can put this
    straight into a log or an error banner without leaking or bloating it.
    """


class JSONResponseError(JSONParseError):
    """`json` could not decode the response at all.

    Wraps the stdlib's own `json.JSONDecodeError` rather than replacing it:
    `msg`, `lineno`, `colno`, and `pos` are exactly what `json` computed, so
    they point at the real syntax break. `excerpt` is new — the text around
    `pos`, with `[HERE]` marking the exact failing character, since a bare
    position is not something a human (or a re-prompted model) can act on.
    """

    def __init__(self, decode_error: json.JSONDecodeError, *, text: str) -> None:
        self.msg = decode_error.msg
        self.lineno = decode_error.lineno
        self.colno = decode_error.colno
        self.pos = decode_error.pos
        self.text_length = len(text)
        self.excerpt = _excerpt_around(text, decode_error.pos)
        super().__init__(
            f"{self.msg} at line {self.lineno} column {self.colno} "
            f"(char {self.pos}); response is {self.text_length} chars; "
            f"around: {self.excerpt!r}"
        )


class MultipleJSONObjectsError(JSONParseError):
    """The response contains more than one top-level JSON object.

    Ambiguous on purpose: nothing here guesses which one the caller meant,
    since guessing wrong would silently feed the pipeline the wrong shot,
    scene, or bible.
    """

    def __init__(self, text: str) -> None:
        self.text_length = len(text)
        super().__init__(
            f"response contains more than one top-level JSON object "
            f"({self.text_length} chars total); expected exactly one"
        )


def _excerpt_around(text: str, pos: int) -> str:
    start = max(0, pos - _EXCERPT_RADIUS)
    end = min(len(text), pos + _EXCERPT_RADIUS)
    marker = pos - start
    window = text[start:end]
    prefix = "…" if start > 0 else ""
    suffix = "…" if end < len(text) else ""
    return f"{prefix}{window[:marker]}[HERE]{window[marker:]}{suffix}"


def _find_second_object(remainder: str, decoder: json.JSONDecoder) -> bool:
    """Whether `remainder` contains another complete top-level JSON object.

    Scans past every `{` that turns out to be incidental — mentioned in
    trailing prose, not the start of real JSON — rather than concluding
    "ambiguous" on the first stray brace character.
    """
    search_from = 0
    while True:
        candidate = remainder.find("{", search_from)
        if candidate == -1:
            return False
        try:
            decoder.raw_decode(remainder, candidate)
        except json.JSONDecodeError:
            search_from = candidate + 1
            continue
        return True


def _require_object(obj: Any, *, text: str, pos: int) -> dict[str, Any]:
    """The schema is always an object; valid-but-wrong-shape JSON (a bare
    array, string, or number) is a decode failure like any other, reported
    at `pos` — the start of the value — rather than silently accepted.
    """
    if isinstance(obj, dict):
        return obj
    raise JSONResponseError(
        json.JSONDecodeError(
            f"expected a JSON object, got {type(obj).__name__}", text, pos
        ),
        text=text,
    )


def _extract_single_object(text: str) -> dict[str, Any]:
    """Find exactly one JSON object in `text`, tolerating surrounding prose.

    Used only once a strict `json.loads` on the whole (fence-stripped)
    string has already failed — the common case of a well-formed response
    needs none of this. From here: locate the first `{`, decode a complete
    object starting there with `json.JSONDecoder.raw_decode` (this is a real
    parse, not a brace-matching regex, so it is correct in the presence of
    braces inside strings), then confirm nothing after it is a second object
    before accepting the first.
    """
    decoder = json.JSONDecoder()
    start = text.find("{")
    if start == -1:
        raise JSONResponseError(
            json.JSONDecodeError("no JSON object found in response", text, 0), text=text
        )

    try:
        obj, end = decoder.raw_decode(text, start)
    except json.JSONDecodeError as exc:
        raise JSONResponseError(exc, text=text) from exc

    obj = _require_object(obj, text=text, pos=start)

    if _find_second_object(text[end:], decoder):
        raise MultipleJSONObjectsError(text)

    return obj


def parse_json_response(text: str) -> dict[str, Any]:
    """Reduce an LLM response to exactly one JSON object.

    Two tiers, cheapest first:

    1. Strip ```json ... ``` fences (and bare ``` fences) and surrounding
       whitespace, then try a strict `json.loads`. This is the expected
       path for a provider that honours `response_format: json_object` —
       most of the time, nothing past this point ever runs.
    2. If that fails, fall back to `_extract_single_object`, which tolerates
       brief prose before or after the object but still performs a real
       parse rather than a "first { to last }" regex — a greedy brace match
       would happily swallow a second, unrelated object, or truncate at a
       brace that only looks structural because it sits inside a string.

    Either tier can produce syntactically valid JSON that is not an object
    (a bare array, say) — `_require_object` rejects that the same way as
    malformed JSON, since the schema this is always parsing into is an
    object.

    Raises `JSONResponseError` (invalid JSON, or valid JSON of the wrong
    shape) or `MultipleJSONObjectsError` (more than one top-level object)
    rather than a bare `json.JSONDecodeError`, so a caller has enough to
    build an actionable message instead of restating "the model didn't
    return JSON."

    Diagnostics (`text_length`, `pos`, the excerpt) are reported against
    `cleaned` — what was actually decoded — not the raw argument, so a
    reported position always lands inside the text the excerpt is drawn
    from; the only thing fence-stripping ever removes is the fence markup
    itself.
    """
    cleaned = _JSON_FENCE_RE.sub("", text.strip()).strip()
    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError:
        return _extract_single_object(cleaned)
    return _require_object(result, text=cleaned, pos=0)


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
