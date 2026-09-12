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


def _reply(text: str, *, finish_reason: str | None = None) -> dict:
    choice: dict = {"message": {"role": "assistant", "content": text}}
    if finish_reason is not None:
        choice["finish_reason"] = finish_reason
    return {"choices": [choice]}


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


def test_harmless_prose_around_the_object_is_tolerated():
    """The full request/response path benefits from parse_json_response's
    prose-tolerant extraction, not just the parser in isolation."""
    client = _client([_reply('Sure, here you go:\n{"title": "Chatty"}\nHope that helps!')])
    assert client.complete_json(task="director", system="s", user="u")["title"] == "Chatty"


def test_a_normal_valid_response_makes_exactly_one_request():
    transport = _Transport([_reply('{"title": "One Shot"}')])
    client = OpenRouterLLMClient(api_key="k", transport=transport)
    client.complete_json(task="director", system="s", user="u")
    assert len(transport.calls) == 1


# ---------------------------------------------------------------------- #
# Failure modes                                                           #
# ---------------------------------------------------------------------- #


def test_non_json_reply_gets_one_retry_then_fails_with_both_attempts_shown():
    """Mid-pipeline, what the model actually said beats a bare decode error —
    and a refusal is "malformed structured output" like any other, so it
    earns exactly one correction retry before MovieCrew gives up."""
    client = _client(
        [
            _reply("I'm afraid I can't help with that."),
            _reply("I'm afraid I can't help with that."),
        ]
    )
    with pytest.raises(LLMError, match="can't help"):
        client.complete_json(task="director", system="s", user="u")


def test_error_payload_is_surfaced():
    client = _client([{"error": {"message": "insufficient credits"}}])
    with pytest.raises(LLMError, match="insufficient credits"):
        client.complete_json(task="writer", system="s", user="u")


def test_an_error_payload_is_not_retried():
    """The model/API itself failed before ever producing text — a
    correction instruction cannot fix that, so it must not spend a second
    request pretending otherwise."""
    transport = _Transport([{"error": {"message": "insufficient credits"}}])
    client = OpenRouterLLMClient(api_key="k", transport=transport)
    with pytest.raises(LLMError):
        client.complete_json(task="writer", system="s", user="u")
    assert len(transport.calls) == 1


def test_empty_choices_is_an_error_not_a_crash():
    client = _client([{"choices": []}])
    with pytest.raises(LLMError, match="no choices"):
        client.complete_json(task="writer", system="s", user="u")


def test_empty_choices_is_not_retried():
    transport = _Transport([{"choices": []}])
    client = OpenRouterLLMClient(api_key="k", transport=transport)
    with pytest.raises(LLMError):
        client.complete_json(task="writer", system="s", user="u")
    assert len(transport.calls) == 1


def test_transport_failure_propagates_as_llm_error():
    client = _client([LLMError("POST … unreachable: timed out")])
    with pytest.raises(LLMError, match="unreachable"):
        client.complete_json(task="writer", system="s", user="u")


def test_transport_failure_is_not_retried():
    """A network/auth/rate-limit failure is not "malformed structured
    output" — retrying it here would just be an undocumented second network
    call for a problem this mechanism cannot fix."""
    transport = _Transport([LLMError("POST … unreachable: timed out")])
    client = OpenRouterLLMClient(api_key="k", transport=transport)
    with pytest.raises(LLMError):
        client.complete_json(task="writer", system="s", user="u")
    assert len(transport.calls) == 1


# ---------------------------------------------------------------------- #
# Truncation: reported explicitly, never spent on the correction retry    #
# ---------------------------------------------------------------------- #


def test_truncated_response_is_reported_as_truncation_not_bad_json():
    truncated = '{"title": "Oumuamua", "logline": "When a shoebox-sized ship'
    client = _client([_reply(truncated, finish_reason="length")])
    with pytest.raises(LLMError, match=r"truncated"):
        client.complete_json(task="director", system="s", user="u")


def test_truncated_response_names_the_finish_reason_and_the_current_limit():
    truncated = '{"title": "Oumuamua"'
    client = _client([_reply(truncated, finish_reason="length")], max_tokens=8192)
    with pytest.raises(LLMError, match=r"finish_reason='length'") as excinfo:
        client.complete_json(task="director", system="s", user="u")
    assert "8192" in str(excinfo.value)


def test_a_truncated_response_does_not_spend_the_correction_retry():
    """Retrying a token-limit cutoff with the same max_tokens would just
    reproduce the same truncation — the budget, not the wording, is wrong."""
    transport = _Transport(
        [_reply('{"title": "Oumuamua"', finish_reason="length")]
    )
    client = OpenRouterLLMClient(api_key="k", transport=transport)
    with pytest.raises(LLMError, match="truncated"):
        client.complete_json(task="director", system="s", user="u")
    assert len(transport.calls) == 1


def test_truncation_on_the_retry_attempt_is_also_reported_as_truncation():
    """If the first failure was ordinary malformed JSON but the *retry*
    itself gets cut off, that is still a truncation — not a second
    "did not return JSON" collapse."""
    client = _client(
        [
            _reply('{"title": "First" "oops"}'),  # malformed, not truncated
            _reply('{"title": "Retry response', finish_reason="length"),
        ]
    )
    with pytest.raises(LLMError, match=r"truncated.*attempt 2/2"):
        client.complete_json(task="director", system="s", user="u")


# ---------------------------------------------------------------------- #
# The correction retry                                                    #
# ---------------------------------------------------------------------- #


def test_malformed_first_response_then_a_valid_retry_succeeds():
    client = _client(
        [
            _reply('{"title": "First" "oops"}'),
            _reply('{"title": "Second, corrected"}'),
        ]
    )
    result = client.complete_json(task="director", system="s", user="u")
    assert result == {"title": "Second, corrected"}


def test_the_retry_makes_exactly_two_requests():
    transport = _Transport(
        [
            _reply('{"title": "First" "oops"}'),
            _reply('{"title": "Second, corrected"}'),
        ]
    )
    client = OpenRouterLLMClient(api_key="k", transport=transport)
    client.complete_json(task="director", system="s", user="u")
    assert len(transport.calls) == 2


def test_the_retry_keeps_the_system_prompt_and_appends_a_correction_to_user():
    transport = _Transport(
        [
            _reply('{"title": "First" "oops"}'),
            _reply('{"title": "Second, corrected"}'),
        ]
    )
    client = OpenRouterLLMClient(api_key="k", transport=transport)
    client.complete_json(task="director", system="the system prompt", user="the user turn")

    retry_body = transport.calls[1]["body"]
    assert retry_body["messages"][0] == {"role": "system", "content": "the system prompt"}
    retry_user = retry_body["messages"][1]["content"]
    assert retry_user.startswith("the user turn")
    assert "could not be parsed" in retry_user
    assert "No markdown fence" in retry_user


def test_the_retry_still_asks_for_a_json_object_outright():
    """response_format is not dropped just because the provider ignored it
    once — a provider that honours it is still better off with it set."""
    transport = _Transport(
        [
            _reply('{"title": "First" "oops"}'),
            _reply('{"title": "Second, corrected"}'),
        ]
    )
    client = OpenRouterLLMClient(api_key="k", transport=transport)
    client.complete_json(task="director", system="s", user="u")
    assert transport.calls[1]["body"]["response_format"] == {"type": "json_object"}


def test_malformed_first_and_second_response_fails_with_both_diagnostics():
    client = _client(
        [
            _reply('{"title": "First" "oops"}'),
            _reply('{"title": "Second" "also broken"}'),
        ]
    )
    with pytest.raises(LLMError) as excinfo:
        client.complete_json(task="director", system="s", user="u")
    message = str(excinfo.value)
    assert "First attempt:" in message
    assert "Retry attempt:" in message
    # Both attempts' own line/column diagnostics, not a bare "did not
    # return JSON" restating the model's words.
    assert message.count("column") == 2


def test_malformed_twice_makes_exactly_two_requests_not_more():
    transport = _Transport(
        [
            _reply('{"title": "First" "oops"}'),
            _reply('{"title": "Second" "also broken"}'),
        ]
    )
    client = OpenRouterLLMClient(api_key="k", transport=transport)
    with pytest.raises(LLMError):
        client.complete_json(task="director", system="s", user="u")
    assert len(transport.calls) == 2


def test_multiple_json_objects_is_treated_as_malformed_and_gets_a_retry():
    """MovieCrew's own parser refusing an ambiguous response is still
    "malformed structured output" from the caller's point of view."""
    client = _client(
        [
            _reply('{"title": "First"} {"title": "Second"}'),
            _reply('{"title": "Corrected"}'),
        ]
    )
    result = client.complete_json(task="director", system="s", user="u")
    assert result == {"title": "Corrected"}


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
