"""Tests for the OpenRouter-backed LLM client.

Fully offline: the transport is injected, so no key and no network are
needed on any path.
"""

from __future__ import annotations

import pytest

from moviecrew.llm_openrouter import (
    API_KEY_ENV,
    DEFAULT_MODEL,
    LLMError,
    OpenRouterLLMClient,
)


class _Transport:
    """Records calls and replays canned payloads in order."""

    def __init__(self, payloads):
        self._payloads = list(payloads)
        self.calls: list[dict] = []

    def __call__(self, method, url, headers, body):
        self.calls.append({"method": method, "url": url, "headers": headers, "body": body})
        if not self._payloads:
            raise AssertionError("transport called more times than it has payloads")
        payload = self._payloads.pop(0)
        if isinstance(payload, Exception):
            raise payload
        return payload


def _reply(text: str) -> dict:
    return {"choices": [{"message": {"role": "assistant", "content": text}}]}


def _client(payloads, **kwargs) -> OpenRouterLLMClient:
    return OpenRouterLLMClient(transport=_Transport(payloads), **kwargs)


# ---------------------------------------------------------------------- #
# Construction and auth                                                   #
# ---------------------------------------------------------------------- #


def test_missing_key_raises_a_message_naming_the_variable(monkeypatch):
    monkeypatch.delenv(API_KEY_ENV, raising=False)
    with pytest.raises(LLMError, match=API_KEY_ENV):
        OpenRouterLLMClient()


def test_injected_transport_needs_no_key(monkeypatch):
    monkeypatch.delenv(API_KEY_ENV, raising=False)
    assert _client([]).name == "openrouter"


def test_key_is_sent_as_a_bearer_header():
    transport = _Transport([_reply("{}")])
    client = OpenRouterLLMClient(api_key="sk-test", transport=transport)
    client.complete_json(task="director", system="s", user="u")
    assert transport.calls[0]["headers"]["Authorization"] == "Bearer sk-test"


def test_key_never_appears_in_the_url():
    transport = _Transport([_reply("{}")])
    client = OpenRouterLLMClient(api_key="sk-secret", transport=transport)
    client.complete_json(task="writer", system="s", user="u")
    assert "sk-secret" not in transport.calls[0]["url"]


# ---------------------------------------------------------------------- #
# Request shape                                                           #
# ---------------------------------------------------------------------- #


def test_every_task_runs_on_sonnet_5_by_default():
    """One model for the whole crew keeps a project's voice consistent."""
    client = _client([])
    for task in ("director", "writer", "designer", "cinematographer", "editor",
                 "prompter", "continuity"):
        assert client.build_request(task=task, system="s", user="u")["model"] == DEFAULT_MODEL

    assert DEFAULT_MODEL == "anthropic/claude-sonnet-5"


def test_model_is_overridable():
    client = _client([], model="anthropic/claude-opus-5")
    assert client.build_request(task="director", system="s", user="u")["model"] == (
        "anthropic/claude-opus-5"
    )


def test_system_and_user_become_two_messages():
    body = _client([]).build_request(task="writer", system="be terse", user="a lighthouse")
    assert body["messages"] == [
        {"role": "system", "content": "be terse"},
        {"role": "user", "content": "a lighthouse"},
    ]


def test_json_object_is_requested_outright():
    body = _client([]).build_request(task="writer", system="s", user="u")
    assert body["response_format"] == {"type": "json_object"}


def test_posts_to_the_chat_completions_endpoint():
    transport = _Transport([_reply("{}")])
    OpenRouterLLMClient(api_key="k", transport=transport).complete_json(
        task="editor", system="s", user="u"
    )
    call = transport.calls[0]
    assert call["method"] == "POST"
    assert call["url"].endswith("/chat/completions")


# ---------------------------------------------------------------------- #
# Response parsing                                                        #
# ---------------------------------------------------------------------- #


def test_plain_json_is_parsed():
    client = _client([_reply('{"title": "Salt and Light"}')])
    assert client.complete_json(task="director", system="s", user="u") == {
        "title": "Salt and Light"
    }


def test_fenced_json_is_parsed():
    """Providers that ignore response_format still wrap answers in fences."""
    client = _client([_reply('```json\n{"title": "Fenced"}\n```')])
    assert client.complete_json(task="director", system="s", user="u")["title"] == "Fenced"


def test_content_block_list_is_parsed():
    """Some providers return Anthropic-shaped blocks rather than a string."""
    payload = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": [{"type": "text", "text": '{"title": "Blocks"}'}],
                }
            }
        ]
    }
    client = _client([payload])
    assert client.complete_json(task="director", system="s", user="u")["title"] == "Blocks"


# ---------------------------------------------------------------------- #
# Failure modes                                                           #
# ---------------------------------------------------------------------- #


def test_non_json_reply_fails_with_the_models_own_words():
    """Mid-pipeline, what the model actually said beats a bare decode error."""
    client = _client([_reply("I'm afraid I can't help with that.")])
    with pytest.raises(LLMError, match="can't help"):
        client.complete_json(task="director", system="s", user="u")


def test_error_payload_is_surfaced():
    client = _client([{"error": {"message": "insufficient credits"}}])
    with pytest.raises(LLMError, match="insufficient credits"):
        client.complete_json(task="writer", system="s", user="u")


def test_empty_choices_is_an_error_not_a_crash():
    client = _client([{"choices": []}])
    with pytest.raises(LLMError, match="no choices"):
        client.complete_json(task="writer", system="s", user="u")


def test_transport_failure_propagates_as_llm_error():
    client = _client([LLMError("POST … unreachable: timed out")])
    with pytest.raises(LLMError, match="unreachable"):
        client.complete_json(task="writer", system="s", user="u")


# ---------------------------------------------------------------------- #
# It really is an LLMClient                                               #
# ---------------------------------------------------------------------- #


def test_satisfies_the_llm_client_interface():
    from moviecrew.llm import LLMClient

    assert isinstance(_client([]), LLMClient)


def test_drives_the_whole_crew():
    """The agents only ever call complete_json, so a canned reply per call
    is enough to prove the client is wired in correctly."""
    from moviecrew.crew import MovieCrew
    from moviecrew.mock import MockLLMClient

    canned = MockLLMClient()

    class Replay(OpenRouterLLMClient):
        """Answers with the mock's payloads, over the OpenRouter code path."""

        def __init__(self):
            super().__init__(api_key="k", transport=self._replay)

        def _replay(self, method, url, headers, body):
            task = self._task
            system = body["messages"][0]["content"]
            user = body["messages"][1]["content"]
            import json

            answer = canned.complete_json(task=task, system=system, user=user)
            return _reply(json.dumps(answer))

        def complete_json(self, *, task, system, user):
            self._task = task
            return super().complete_json(task=task, system=system, user=user)

    project = MovieCrew(Replay()).make("A keeper and a sea spirit.")
    assert project.title
    assert project.scenes
