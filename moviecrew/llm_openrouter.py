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
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Callable, Optional

from .llm import LLMClient, parse_json_response

API_ROOT = "https://openrouter.ai/api/v1"
API_KEY_ENV = "OPENROUTER_API_KEY"

# OpenRouter namespaces a model by its provider. `anthropic/claude-sonnet-5`
# is the same Claude Sonnet 5 the first-party API calls `claude-sonnet-5`.
DEFAULT_MODEL = "anthropic/claude-sonnet-5"

# Per-task overrides, for callers who want the Anthropic path's shape back.
# Empty by default: everything runs on DEFAULT_MODEL.
TASK_MODEL_ROUTING: dict[str, str] = {}

DEFAULT_MAX_TOKENS = 8192


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


def _text_of(payload: dict[str, Any]) -> str:
    """The assistant's message text, whichever shape it came back in.

    OpenRouter normalises most providers to a plain string, but some return
    the Anthropic-style list of content blocks. Both are handled rather than
    assumed, because the difference only shows up against a live provider.
    """
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise LLMError(f"no choices in response: {json.dumps(payload)[:300]}")

    message = choices[0].get("message") or {}
    content = message.get("content")

    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") in (None, "text")
        ]
        if parts:
            return "".join(parts)

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

    def complete_json(self, *, task: str, system: str, user: str) -> dict[str, Any]:
        body = self.build_request(task=task, system=system, user=user)
        payload = self._transport(
            "POST", f"{self.api_root}/chat/completions", self._headers(), body
        )
        if isinstance(payload.get("error"), dict):
            message = payload["error"].get("message", "unknown error")
            raise LLMError(f"{self.model_for_task(task)} failed: {message}")

        text = _text_of(payload)
        try:
            return parse_json_response(text)
        except json.JSONDecodeError as exc:
            # The agents all expect JSON. Failing with the model's actual
            # words is far more useful mid-pipeline than a bare decode error.
            raise LLMError(
                f"{self.model_for_task(task)} did not return JSON for task "
                f"{task!r}: {text[:300]}"
            ) from exc
