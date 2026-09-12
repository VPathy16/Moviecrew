"""LLMClient backed by OpenRouter's chat-completions API.

One key for both halves of the pipeline. The render side already goes
through OpenRouter (`render_openrouter.py`), and routing the agents there
too means a single credential, a single bill, and a model that is
configuration rather than a code change.

HTTP goes through `urllib` from the standard library rather than
`requests` or an SDK. That is the same deliberate choice `render_openrouter`
makes: MovieCrew's core has no third-party imports, which is what lets the
whole package drop into Blender's bundled Python with nothing to install.

The key is read from $OPENROUTER_API_KEY server-side and never travels in a
response. `transport` is injectable, which is how the tests exercise every
path with no network and no key.

Every task runs on one model by default. The Anthropic path routes per task
(Opus for the director, Haiku for the editor); here the whole crew runs on
Sonnet 5 unless a caller says otherwise, because a single model keeps the
voice of a project consistent across agents and the price predictable.

`complete_json` distinguishes four ways a completion can fail rather than
reporting all of them as "did not return JSON": the request itself failing
(transport, auth, rate limit — surfaced immediately, never retried here),
the model being cut off by its own token limit (`finish_reason == "length"`
— a truncation error naming the limit, since retrying would just spend the
same budget on the same failure), a complete but malformed response (parsed
with `llm.parse_json_response`'s real JSON-aware extraction, not a greedy
brace-matching regex — retried exactly once with a short correction
instruction), and MovieCrew's own parser rejecting an ambiguous response.
See `llm.JSONParseError` and its subclasses for the diagnostics — an exact
line/column/character position and a bounded excerpt around the break, not
a blind first-300-characters truncation of what might be a very long
response.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Callable, Optional

from .llm import JSONParseError, LLMClient, parse_json_response

API_ROOT = "https://openrouter.ai/api/v1"
API_KEY_ENV = "OPENROUTER_API_KEY"

# OpenRouter namespaces a model by its provider. `anthropic/claude-sonnet-5`
# is the same Claude Sonnet 5 the first-party API calls `claude-sonnet-5`.
DEFAULT_MODEL = "anthropic/claude-sonnet-5"

# Per-task overrides, for callers who want the Anthropic path's shape back.
# Empty by default: everything runs on DEFAULT_MODEL.
TASK_MODEL_ROUTING: dict[str, str] = {}

DEFAULT_MAX_TOKENS = 8192

# Sent back as the user turn's own trailer on the one retry a malformed
# structured output gets. Deliberately says nothing about *why* parsing
# failed — the point is a clean second attempt, not a debugging session the
# model cannot actually have with itself.
_CORRECTION_INSTRUCTION = (
    "Your previous response could not be parsed. Return ONLY one valid JSON "
    "object matching the requested schema. No markdown fence, commentary, "
    "or trailing text."
)

# OpenRouter's own name for "the response was cut off by a token limit",
# passed through from whichever provider actually served the request.
_TRUNCATED_FINISH_REASON = "length"


class LLMError(RuntimeError):
    """A completion that could not be produced."""


def _urllib_transport(
    method: str, url: str, headers: dict[str, str], body: Optional[dict]
) -> dict[str, Any]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            return json.loads(response.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:400]
        raise LLMError(f"{method} {url} failed ({exc.code}): {detail}") from exc
    except urllib.error.URLError as exc:
        raise LLMError(f"{method} {url} unreachable: {exc.reason}") from exc


def _text_and_finish_reason(payload: dict[str, Any]) -> tuple[str, Optional[str]]:
    """The assistant's message text and why the model stopped, together.

    They come from the same `choices[0]` and are always needed together: a
    parse failure is a different problem depending on whether `finish_reason`
    says the response is even complete. OpenRouter normalises most providers'
    text to a plain string, but some return the Anthropic-style list of
    content blocks; both are handled rather than assumed, because the
    difference only shows up against a live provider.
    """
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise LLMError(f"no choices in response: {json.dumps(payload)[:300]}")

    choice = choices[0]
    finish_reason = choice.get("finish_reason")
    message = choice.get("message") or {}
    content = message.get("content")

    if isinstance(content, str):
        return content, finish_reason
    if isinstance(content, list):
        parts = [
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") in (None, "text")
        ]
        if parts:
            return "".join(parts), finish_reason

    raise LLMError(f"no text content in response: {json.dumps(payload)[:300]}")


class OpenRouterLLMClient(LLMClient):
    """Every agent's completions, routed through OpenRouter."""

    name = "openrouter"

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        api_root: str = API_ROOT,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        transport: Optional[Callable[..., dict[str, Any]]] = None,
        referer: str = "https://github.com/VPathy16/Moviecrew",
        title: str = "MovieCrew",
    ) -> None:
        self.model = model
        self.api_root = api_root.rstrip("/")
        self._max_tokens = max_tokens
        self._transport = transport or _urllib_transport
        self._referer = referer
        self._title = title

        # An injected transport is the test seam, and needs no key.
        self._api_key = api_key or os.environ.get(API_KEY_ENV, "")
        if not self._api_key and transport is None:
            raise LLMError(
                f"OpenRouterLLMClient needs an API key: set {API_KEY_ENV} in the "
                "environment, or pass api_key=... explicitly."
            )

    def model_for_task(self, task: str) -> str:
        return TASK_MODEL_ROUTING.get(task, self.model)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self._referer,
            "X-Title": self._title,
        }

    def build_request(self, *, task: str, system: str, user: str) -> dict[str, Any]:
        """The request body for one completion. Pure, so tests can assert on it.

        `response_format` asks for a JSON object outright. Providers that
        honour it stop wrapping the answer in prose or fences; those that
        ignore it are still handled, because `parse_json_response` strips
        fences on the way out.
        """
        return {
            "model": self.model_for_task(task),
            "max_tokens": self._max_tokens,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": {"type": "json_object"},
        }

    def _call(self, *, task: str, system: str, user: str) -> tuple[str, Optional[str]]:
        """One request to the provider: build it, send it, surface an
        API-level error immediately, and return the raw text plus why the
        model stopped. Never touches JSON parsing — a transport failure or
        an `error` payload is not something a correction retry can fix, so
        neither is caught by the retry logic in `complete_json`.
        """
        body = self.build_request(task=task, system=system, user=user)
        payload = self._transport(
            "POST", f"{self.api_root}/chat/completions", self._headers(), body
        )
        if isinstance(payload.get("error"), dict):
            message = payload["error"].get("message", "unknown error")
            raise LLMError(f"{self.model_for_task(task)} failed: {message}")
        return _text_and_finish_reason(payload)

    def _truncation_error(
        self, *, task: str, text: str, finish_reason: str, attempt: int
    ) -> LLMError:
        tail = text[-200:]
        return LLMError(
            f"{self.model_for_task(task)} output for task {task!r} was truncated "
            f"(finish_reason={finish_reason!r}) before valid JSON completed, on "
            f"attempt {attempt}/2; increase max_tokens (currently "
            f"{self._max_tokens}) or ask for a smaller response. Response was "
            f"{len(text)} chars; tail: {tail!r}"
        )

    def complete_json(self, *, task: str, system: str, user: str) -> dict[str, Any]:
        """Run one completion for `task`, correcting exactly one kind of
        failure: a response that reached us, is not obviously truncated, and
        still failed to parse. MovieCrew distinguishes four failures rather
        than collapsing them into "did not return JSON":

          - the request itself failed (`_call` raises `LLMError` directly —
            transport/auth/rate-limit, never retried here)
          - the model was cut off by its token limit (`finish_reason ==
            "length"` — reported as a truncation error, retry would just
            spend the same budget on the same failure)
          - the model returned complete but malformed structured output
            (parsing failed, not truncated — the one case retried, once,
            with a correction instruction)
          - MovieCrew's own parser rejected the response (ambiguous JSON —
            `parse_json_response` raising `MultipleJSONObjectsError` is this
            case, and is retried the same way: it is still "malformed
            structured output" from the caller's point of view)
        """
        text, finish_reason = self._call(task=task, system=system, user=user)
        try:
            return parse_json_response(text)
        except JSONParseError as first_error:
            if finish_reason == _TRUNCATED_FINISH_REASON:
                raise self._truncation_error(
                    task=task, text=text, finish_reason=finish_reason, attempt=1
                ) from first_error

            retry_text, retry_finish_reason = self._call(
                task=task, system=system, user=f"{user}\n\n{_CORRECTION_INSTRUCTION}"
            )
            try:
                return parse_json_response(retry_text)
            except JSONParseError as retry_error:
                if retry_finish_reason == _TRUNCATED_FINISH_REASON:
                    raise self._truncation_error(
                        task=task,
                        text=retry_text,
                        finish_reason=retry_finish_reason,
                        attempt=2,
                    ) from retry_error
                # The agents all expect JSON. Both attempts' own diagnostics
                # (line/column/excerpt) beat a bare decode error mid-pipeline.
                raise LLMError(
                    f"{self.model_for_task(task)} did not return parseable JSON "
                    f"for task {task!r} after 1 correction retry.\n"
                    f"First attempt: {first_error}\n"
                    f"Retry attempt: {retry_error}"
                ) from retry_error
