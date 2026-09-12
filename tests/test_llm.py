"""Tests for parse_json_response: reducing an LLM response to one JSON
object, with real diagnostics when that fails.

The invariant under test: a caller must be able to tell "the response was
not JSON at all" from "the response contained more than one JSON object"
from "the response parsed fine" — and for the first case, get back exactly
where and why, not a blind slice of the first N characters.
"""

from __future__ import annotations

import json

import pytest

from moviecrew.llm import (
    _JSON_FENCE_RE,
    JSONParseError,
    JSONResponseError,
    MultipleJSONObjectsError,
    parse_json_response,
)


def _cleaned(text: str) -> str:
    """What parse_json_response actually decodes, after fence-stripping —
    diagnostics (text_length, pos, the excerpt) are reported against this,
    not the raw argument, so positions always land inside the excerpted
    text."""
    return _JSON_FENCE_RE.sub("", text.strip()).strip()


# ---------------------------------------------------------------------- #
# The happy paths                                                         #
# ---------------------------------------------------------------------- #


def test_plain_json_object():
    assert parse_json_response('{"title": "Salt and Light"}') == {
        "title": "Salt and Light"
    }


def test_fenced_with_json_language_tag():
    assert parse_json_response('```json\n{"title": "Fenced"}\n```') == {
        "title": "Fenced"
    }


def test_fenced_with_no_language_tag():
    assert parse_json_response('```\n{"title": "Fenced"}\n```') == {"title": "Fenced"}


def test_surrounding_whitespace_is_ignored():
    assert parse_json_response('  \n {"title": "Padded"}\n  ') == {"title": "Padded"}


def test_harmless_leading_prose():
    """A model that answers a JSON-only instruction with a sentence first —
    the object itself is still complete and unambiguous."""
    text = 'Sure, here is the plan:\n{"title": "With Preamble"}'
    assert parse_json_response(text) == {"title": "With Preamble"}


def test_harmless_trailing_prose():
    text = '{"title": "With Trailer"}\nLet me know if you would like changes!'
    assert parse_json_response(text) == {"title": "With Trailer"}


def test_leading_and_trailing_prose_together():
    text = 'Here you go:\n{"title": "Both"}\nHope that helps!'
    assert parse_json_response(text) == {"title": "Both"}


def test_a_brace_inside_trailing_prose_is_not_mistaken_for_a_second_object():
    """The regex this replaces would take the first `{` to the *last* `}` —
    a stray brace in prose must not pull in unrelated text or reject a
    perfectly good single-object response."""
    text = '{"title": "One"}\nNote: keep braces {like this} out of titles.'
    assert parse_json_response(text) == {"title": "One"}


def test_a_brace_pair_that_is_not_valid_json_in_trailing_prose_is_ignored():
    text = '{"title": "One"}\nSee also: {not json}'
    assert parse_json_response(text) == {"title": "One"}


def test_nested_objects_and_arrays_are_not_mistaken_for_multiple_objects():
    text = '{"title": "One", "scenes": [{"id": "s1"}, {"id": "s2"}]}'
    assert parse_json_response(text) == {
        "title": "One",
        "scenes": [{"id": "s1"}, {"id": "s2"}],
    }


# ---------------------------------------------------------------------- #
# Malformed JSON: exact diagnostics, not a 300-character guess            #
# ---------------------------------------------------------------------- #


def test_truncated_json_raises_with_position_and_excerpt():
    """The exact shape of the bug report that started this: a response cut
    off mid-string, still opening with a fenced JSON object."""
    text = (
        '```json\n{\n  "title": "Oumuamua: The Chennai Incident",\n'
        '  "logline": "When a shoebox-sized ship jettisoned from the '
        "interstellar object Oumuamua knocks out a young IT worker in "
        "Madras, he wakes up clutching a strange alien egg that grants him "
        "extraordinary powers—forcing him to outrun a secret agency"
    )
    with pytest.raises(JSONResponseError) as excinfo:
        parse_json_response(text)

    error = excinfo.value
    assert error.msg  # json's own message, e.g. "Unterminated string ..."
    assert error.lineno >= 1
    assert error.colno >= 1
    assert error.pos > 0
    assert error.text_length == len(_cleaned(text))
    assert "[HERE]" in error.excerpt
    # json reports "unterminated string" at the string's *opening* quote,
    # not at end-of-input where it actually got cut off — so the excerpt
    # window is centred there, not on the far-away tail of the response
    # (the tail is what OpenRouterLLMClient's own truncation error shows).
    assert "shoebox-sized ship" in error.excerpt


def test_the_excerpt_is_bounded_not_the_whole_response():
    """However long the response, the excerpt stays small — this is what
    makes it safe to put straight into a log line or an error banner."""
    text = "x" * 5000 + '{"title": "unterminated'
    with pytest.raises(JSONResponseError) as excinfo:
        parse_json_response(text)
    assert len(excinfo.value.excerpt) < 500
    assert excinfo.value.text_length == len(text)


def test_a_decode_error_message_reads_like_the_documented_example():
    text = '{"title": "A", "logline": "B" "outline": []}'
    with pytest.raises(JSONResponseError) as excinfo:
        parse_json_response(text)
    message = str(excinfo.value)
    assert f"at line {excinfo.value.lineno} column {excinfo.value.colno}" in message
    assert f"(char {excinfo.value.pos})" in message
    assert "around:" in message


def test_no_json_object_at_all_is_a_json_response_error_not_a_crash():
    with pytest.raises(JSONResponseError):
        parse_json_response("I'm afraid I can't help with that.")


def test_empty_string_is_a_json_response_error_not_a_crash():
    with pytest.raises(JSONResponseError):
        parse_json_response("")


def test_a_json_array_at_top_level_is_rejected_not_silently_accepted():
    """The schema is always an object; a bare array is a different failure
    from valid-but-wrong-shape, and is reported as such."""
    with pytest.raises(JSONResponseError):
        parse_json_response('["not", "an", "object"]')


# ---------------------------------------------------------------------- #
# Multiple JSON objects: ambiguous, and refused rather than guessed at    #
# ---------------------------------------------------------------------- #


def test_two_complete_objects_are_rejected():
    with pytest.raises(MultipleJSONObjectsError):
        parse_json_response('{"title": "First"} {"title": "Second"}')


def test_two_complete_objects_on_separate_lines_are_rejected():
    with pytest.raises(MultipleJSONObjectsError):
        parse_json_response('{"title": "First"}\n{"title": "Second"}')


def test_multiple_objects_error_names_the_response_length():
    text = '{"a": 1} {"b": 2}'
    with pytest.raises(MultipleJSONObjectsError) as excinfo:
        parse_json_response(text)
    assert excinfo.value.text_length == len(text)


def test_both_parse_failures_share_a_common_base_class():
    """So a caller can catch one type and treat both as 'malformed
    structured output', without conflating them with an unrelated ValueError
    somewhere else in the pipeline."""
    assert issubclass(JSONResponseError, JSONParseError)
    assert issubclass(MultipleJSONObjectsError, JSONParseError)


def test_json_parse_error_is_still_a_value_error():
    """Existing code catching bare ValueError (as json.JSONDecodeError
    always could be caught) keeps working."""
    assert issubclass(JSONParseError, ValueError)


# ---------------------------------------------------------------------- #
# Never leaks more than the excerpt                                       #
# ---------------------------------------------------------------------- #


def test_json_response_error_string_does_not_contain_the_full_response():
    text = "PREFIX_MARKER " * 200 + '{"title": "unterminated'
    with pytest.raises(JSONResponseError) as excinfo:
        parse_json_response(text)
    # The excerpt is bounded; the far-away prefix must not appear whole.
    assert str(excinfo.value).count("PREFIX_MARKER") < 200


def test_json_decode_error_reference_is_preserved_for_chaining():
    """Callers (or their own tests) can still inspect the __cause__ chain
    back to the stdlib's own JSONDecodeError."""
    try:
        parse_json_response('{"title": "unterminated')
    except JSONResponseError as exc:
        assert isinstance(exc.__cause__, json.JSONDecodeError)
    else:
        pytest.fail("expected JSONResponseError")
