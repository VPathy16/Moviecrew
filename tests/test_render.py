"""Tests for the render abstraction and the OpenRouter backend.

Fully offline. `OpenRouterRenderClient` takes an injectable transport, so
every path — submit, poll, fetch, failure — runs with no network and no key.
"""

from __future__ import annotations

import pytest

from moviecrew.render import (
    CostModel,
    FakeRenderClient,
    JobStatus,
    RenderCapabilities,
    RenderJob,
    ShotSpec,
)
from moviecrew.render_openrouter import (
    API_KEY_ENV,
    OpenRouterRenderClient,
    RenderError,
)
from moviecrew.schema import VeoPrompt


# ---------------------------------------------------------------------- #
# Capabilities                                                            #
# ---------------------------------------------------------------------- #


def test_terminal_statuses():
    assert JobStatus.SUCCEEDED.is_terminal
    assert JobStatus.FAILED.is_terminal
    assert JobStatus.CANCELLED.is_terminal
    assert not JobStatus.RUNNING.is_terminal
    assert not JobStatus.PENDING.is_terminal


def test_clamp_duration_respects_the_ceiling():
    caps = RenderCapabilities(max_duration_s=8)
    assert caps.clamp_duration(30) == 8
    assert caps.clamp_duration(4) == 4
    assert caps.clamp_duration(0) == 1


# ---------------------------------------------------------------------- #
# ShotSpec                                                                #
# ---------------------------------------------------------------------- #


def test_shot_spec_from_veo_prompt_carries_the_prompt():
    prompt = VeoPrompt(
        shot_id="sc1-sh1",
        prompt="Mara climbs the cliff path.",
        negative_prompt="blurry",
        duration_s=8,
        reference_images=["ch1.png"],
    )
    spec = ShotSpec.from_veo_prompt(prompt)
    assert spec.shot_id == "sc1-sh1"
    assert spec.negative_prompt == "blurry"
    assert spec.reference_images == ["ch1.png"]


def test_shot_spec_overrides_apply():
    prompt = VeoPrompt(shot_id="s1", prompt="p")
    spec = ShotSpec.from_veo_prompt(prompt, reference_video="https://x/take.mp4")
    assert spec.reference_video == "https://x/take.mp4"


def test_shot_spec_defaults_are_not_shared():
    a, b = ShotSpec(shot_id="a", prompt="p"), ShotSpec(shot_id="b", prompt="p")
    a.reference_images.append("x.png")
    assert b.reference_images == []


# ---------------------------------------------------------------------- #
# FakeRenderClient                                                        #
# ---------------------------------------------------------------------- #


def test_fake_succeeds_immediately():
    client = FakeRenderClient()
    job = client.submit(ShotSpec(shot_id="s1", prompt="p"), model="fake/model")
    assert job.status is JobStatus.SUCCEEDED
    assert job.is_terminal


def test_fake_records_what_was_submitted():
    client = FakeRenderClient()
    spec = ShotSpec(shot_id="s1", prompt="p")
    client.submit(spec, model="fake/model")
    assert client.submitted == [(spec, "fake/model")]


def test_fake_can_stay_running_for_a_set_number_of_polls():
    client = FakeRenderClient(pending_polls=2)
    job = client.submit(ShotSpec(shot_id="s1", prompt="p"), model="m")
    assert job.status is JobStatus.RUNNING
    assert client.poll(job.job_id).status is JobStatus.RUNNING
    assert client.poll(job.job_id).status is JobStatus.SUCCEEDED


def test_fake_can_be_made_to_fail():
    client = FakeRenderClient(fail_with="quota exhausted")
    job = client.submit(ShotSpec(shot_id="s1", prompt="p"), model="m")
    assert job.status is JobStatus.FAILED
    assert job.error == "quota exhausted"


def test_fake_poll_of_unknown_job_fails_rather_than_raising():
    assert FakeRenderClient().poll("nope").status is JobStatus.FAILED


def test_fake_fetch_writes_a_file(tmp_path):
    client = FakeRenderClient()
    job = client.submit(ShotSpec(shot_id="s1", prompt="p"), model="m")
    out = client.fetch(job, str(tmp_path / "out.mp4"))
    assert out and (tmp_path / "out.mp4").is_file()


def test_fake_fetch_refuses_an_unfinished_job(tmp_path):
    client = FakeRenderClient(pending_polls=1)
    job = client.submit(ShotSpec(shot_id="s1", prompt="p"), model="m")
    assert client.fetch(job, str(tmp_path / "out.mp4")) is None


def test_fake_spends_nothing_by_default():
    assert FakeRenderClient().estimate_cost(ShotSpec(shot_id="s", prompt="p"), model="m") == 0.0


# ---------------------------------------------------------------------- #
# OpenRouter: construction                                                #
# ---------------------------------------------------------------------- #


def _transport(responses):
    """A transport returning queued responses, recording every call."""
    calls = []

    def transport(method, url, headers, body):
        calls.append({"method": method, "url": url, "headers": headers, "body": body})
        result = responses.pop(0) if responses else {}
        if isinstance(result, Exception):
            raise result
        return result

    transport.calls = calls
    return transport


_MODELS = {
    "data": [
        {
            "id": "bytedance/seedance-2.5",
            "supported_durations": ["4", "8", "12", "30"],
            "supported_resolutions": ["480p", "720p"],
            "supported_aspect_ratios": ["16:9", "9:16"],
            "max_video_references": 3,
            "max_image_references": 9,
            "supports_frame_images": True,
            "pricing": {"video": 0.5},
        }
    ]
}


def test_missing_key_raises_a_message_naming_the_variable(monkeypatch):
    monkeypatch.delenv(API_KEY_ENV, raising=False)
    with pytest.raises(RenderError, match=API_KEY_ENV):
        OpenRouterRenderClient()


def test_injected_transport_needs_no_key(monkeypatch):
    monkeypatch.delenv(API_KEY_ENV, raising=False)
    client = OpenRouterRenderClient(transport=_transport([]))
    assert client.name == "openrouter"


def test_key_is_sent_as_a_bearer_header():
    transport = _transport([_MODELS])
    client = OpenRouterRenderClient(api_key="sk-test", transport=transport)
    client.models()
    assert transport.calls[0]["headers"]["Authorization"] == "Bearer sk-test"


# ---------------------------------------------------------------------- #
# OpenRouter: capabilities                                                #
# ---------------------------------------------------------------------- #


def test_capabilities_read_from_the_model_catalogue():
    client = OpenRouterRenderClient(api_key="k", transport=_transport([_MODELS]))
    caps = client.capabilities("bytedance/seedance-2.5")

    assert caps.max_duration_s == 30
    assert caps.supported_resolutions == ("480p", "720p")
    assert caps.supports_video_reference is True
    assert caps.max_video_references == 3
    assert caps.cost_model.amount == 0.5


def test_capabilities_are_conservative_for_an_unknown_model():
    """Over-promising costs a rejected request after the user has waited."""
    client = OpenRouterRenderClient(api_key="k", transport=_transport([_MODELS]))
    caps = client.capabilities("someone/unlisted")
    assert caps.max_duration_s == 8
    assert caps.supports_video_reference is False


def test_model_catalogue_is_fetched_once():
    transport = _transport([_MODELS, _MODELS])
    client = OpenRouterRenderClient(api_key="k", transport=transport)
    client.models()
    client.models()
    assert len(transport.calls) == 1


# ---------------------------------------------------------------------- #
# OpenRouter: request building                                            #
# ---------------------------------------------------------------------- #


def _client_with_models():
    return OpenRouterRenderClient(api_key="k", transport=_transport([_MODELS]))


def test_take_is_sent_as_a_video_reference():
    """The whole point: the previz clip drives camera motion."""
    body = _client_with_models().build_request(
        ShotSpec(shot_id="s1", prompt="p", reference_video="https://x/take_001.mp4"),
        model="bytedance/seedance-2.5",
    )
    assert body["provider"]["options"]["video_urls"] == ["https://x/take_001.mp4"]


def test_video_reference_is_dropped_for_a_model_that_cannot_take_one():
    """Capability decides, not the backend's name."""
    body = _client_with_models().build_request(
        ShotSpec(shot_id="s1", prompt="p", reference_video="https://x/take.mp4"),
        model="someone/unlisted",
    )
    assert "video_urls" not in body.get("provider", {}).get("options", {})


def test_image_references_are_capped_at_the_model_limit():
    spec = ShotSpec(shot_id="s1", prompt="p", reference_images=[f"{i}.png" for i in range(20)])
    body = _client_with_models().build_request(spec, model="bytedance/seedance-2.5")
    assert len(body["provider"]["options"]["image_urls"]) == 9


def test_duration_is_clamped_to_what_the_model_allows():
    body = _client_with_models().build_request(
        ShotSpec(shot_id="s1", prompt="p", duration_s=120),
        model="bytedance/seedance-2.5",
    )
    assert body["duration"] == 30


def test_request_carries_no_provider_block_when_there_are_no_references():
    body = _client_with_models().build_request(
        ShotSpec(shot_id="s1", prompt="p"), model="bytedance/seedance-2.5"
    )
    assert "provider" not in body


# ---------------------------------------------------------------------- #
# OpenRouter: submit / poll / fetch                                       #
# ---------------------------------------------------------------------- #


def test_submit_returns_a_job_with_the_returned_id():
    transport = _transport([_MODELS, {"id": "vid_1", "status": "queued"}])
    client = OpenRouterRenderClient(api_key="k", transport=transport)
    job = client.submit(ShotSpec(shot_id="sc1-sh1", prompt="p"), model="bytedance/seedance-2.5")

    assert job.job_id == "vid_1"
    assert job.status is JobStatus.PENDING
    assert job.shot_id == "sc1-sh1"
    assert transport.calls[-1]["method"] == "POST"


def test_submit_failure_becomes_a_failed_job_not_an_exception():
    transport = _transport([_MODELS, RenderError("502 upstream")])
    client = OpenRouterRenderClient(api_key="k", transport=transport)
    job = client.submit(ShotSpec(shot_id="s1", prompt="p"), model="bytedance/seedance-2.5")

    assert job.status is JobStatus.FAILED
    assert "502" in job.error


def test_poll_maps_completion_and_cost():
    transport = _transport(
        [{"id": "vid_1", "status": "completed", "video_url": "https://x/o.mp4",
          "usage": {"cost": 0.42}}]
    )
    job = OpenRouterRenderClient(api_key="k", transport=transport).poll("vid_1")

    assert job.status is JobStatus.SUCCEEDED
    assert job.video_url == "https://x/o.mp4"
    assert job.cost == 0.42


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("queued", JobStatus.PENDING),
        ("processing", JobStatus.RUNNING),
        ("success", JobStatus.SUCCEEDED),
        ("error", JobStatus.FAILED),
        ("canceled", JobStatus.CANCELLED),
    ],
)
def test_status_spellings_are_mapped(raw, expected):
    transport = _transport([{"id": "v", "status": raw}])
    assert OpenRouterRenderClient(api_key="k", transport=transport).poll("v").status is expected


def test_unknown_status_is_treated_as_running_not_succeeded():
    """Guessing success would hand a caller a half-finished render."""
    transport = _transport([{"id": "v", "status": "reticulating"}])
    assert OpenRouterRenderClient(api_key="k", transport=transport).poll("v").status is (
        JobStatus.RUNNING
    )


def test_video_url_found_in_a_nested_output():
    transport = _transport([{"id": "v", "status": "completed", "output": [{"url": "https://x/a.mp4"}]}])
    assert OpenRouterRenderClient(api_key="k", transport=transport).poll("v").video_url == (
        "https://x/a.mp4"
    )


def test_poll_failure_becomes_a_failed_job():
    transport = _transport([RenderError("404 no such job")])
    job = OpenRouterRenderClient(api_key="k", transport=transport).poll("gone")
    assert job.status is JobStatus.FAILED
    assert "404" in job.error


def test_fetch_refuses_an_unfinished_job(tmp_path):
    client = OpenRouterRenderClient(api_key="k", transport=_transport([]))
    job = RenderJob(job_id="v", shot_id="s", status=JobStatus.RUNNING)
    assert client.fetch(job, str(tmp_path / "o.mp4")) is None


def test_fetch_refuses_a_job_with_no_url(tmp_path):
    client = OpenRouterRenderClient(api_key="k", transport=_transport([]))
    job = RenderJob(job_id="v", shot_id="s", status=JobStatus.SUCCEEDED)
    assert client.fetch(job, str(tmp_path / "o.mp4")) is None


def test_cost_model_default_is_usd():
    assert CostModel(unit="usd").currency == "USD"
