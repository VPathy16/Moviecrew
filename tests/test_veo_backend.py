"""Tests for VeoBackend, fully offline via an injected FakeClient.

FakeClient mimics the slice of the google-genai SDK VeoBackend.render()
calls: client.models.generate_videos(...), client.operations.get(...) to
poll an operation, and client.files.download(...). None of it touches the
network or needs the google-genai package installed, since VeoBackend
skips the SDK import entirely when a client is injected.
"""

from __future__ import annotations

import os

from moviecrew.schema import VEO_MAX_DURATION_S, VeoPrompt
from moviecrew.video import VeoBackend


class FakeVideo:
    def __init__(self) -> None:
        self.saved_to: str | None = None

    def save(self, path: str) -> None:
        self.saved_to = path


class FakeGeneratedVideo:
    def __init__(self) -> None:
        self.video = FakeVideo()


class FakeResponse:
    def __init__(self) -> None:
        self.generated_videos = [FakeGeneratedVideo()]


class FakeOperation:
    def __init__(self, *, done_after: int, name: str = "op-1") -> None:
        self.name = name
        self._done_after = done_after
        self._polls = 0
        self.done = done_after <= 0
        self.response = FakeResponse() if self.done else None


class FakeOperations:
    def get(self, operation: FakeOperation) -> FakeOperation:
        operation._polls += 1
        if operation._polls >= operation._done_after:
            operation.done = True
            operation.response = FakeResponse()
        return operation


class FakeModels:
    def __init__(self, *, done_after: int = 0, raise_error: Exception | None = None) -> None:
        self.done_after = done_after
        self.raise_error = raise_error
        self.calls: list[dict] = []

    def generate_videos(self, **kwargs):
        if self.raise_error is not None:
            raise self.raise_error
        self.calls.append(kwargs)
        return FakeOperation(done_after=self.done_after)


class FakeFiles:
    def __init__(self) -> None:
        self.downloaded: list[object] = []

    def download(self, *, file) -> None:
        self.downloaded.append(file)


class FakeClient:
    def __init__(self, *, done_after: int = 0, raise_error: Exception | None = None) -> None:
        self.models = FakeModels(done_after=done_after, raise_error=raise_error)
        self.operations = FakeOperations()
        self.files = FakeFiles()


def _prompt(**overrides) -> VeoPrompt:
    fields = dict(
        shot_id="sc1-sh1",
        prompt="Wide shot of a lighthouse keeper climbing a cliff path.",
        negative_prompt="blurry",
        duration_s=4,
        aspect_ratio="16:9",
        reference_images=[],
    )
    fields.update(overrides)
    return VeoPrompt(**fields)


def test_render_succeeds_and_downloads_to_out_dir(tmp_path):
    client = FakeClient(done_after=2)
    backend = VeoBackend(client=client, out_dir=str(tmp_path), poll_interval_s=0)

    result = backend.render(_prompt())

    assert result.status == "succeeded"
    assert result.backend == "veo"
    assert result.uri == os.path.join(str(tmp_path), "sc1-sh1.mp4")

    call = client.models.calls[0]
    assert call["model"] == backend.model
    assert call["config"]["aspect_ratio"] == "16:9"
    assert call["config"]["resolution"] == backend.resolution
    assert call["config"]["duration_seconds"] == 4
    assert client.files.downloaded


def test_reference_images_are_skipped_when_not_real_files(tmp_path):
    client = FakeClient(done_after=1)
    backend = VeoBackend(client=client, out_dir=str(tmp_path), poll_interval_s=0)

    prompt = _prompt(reference_images=["ref-ch1-a", "ref-loc1-a"], duration_s=4)
    result = backend.render(prompt)

    call = client.models.calls[0]
    assert "reference_images" not in call["config"]
    assert result.raw["reference_image_count"] == 0
    assert any("ref-ch1-a" in warning for warning in result.raw["warnings"])
    assert any("ref-loc1-a" in warning for warning in result.raw["warnings"])
    # Placeholders aren't real files, so nothing was sent — duration stays as given.
    assert call["config"]["duration_seconds"] == 4


def test_reference_image_count_is_capped_at_three(tmp_path):
    paths = []
    for i in range(4):
        path = tmp_path / f"ref{i}.png"
        path.write_bytes(b"fake-png-bytes")
        paths.append(str(path))

    client = FakeClient(done_after=1)
    backend = VeoBackend(client=client, out_dir=str(tmp_path), poll_interval_s=0)

    prompt = _prompt(reference_images=paths, duration_s=4)
    result = backend.render(prompt)

    assert result.raw["reference_image_count"] == 3
    assert len(client.models.calls[0]["config"]["reference_images"]) == 3


def test_real_reference_images_coerce_duration_to_eight_with_warning(tmp_path):
    ref_path = tmp_path / "ref0.png"
    ref_path.write_bytes(b"fake-png-bytes")

    client = FakeClient(done_after=1)
    backend = VeoBackend(client=client, out_dir=str(tmp_path), poll_interval_s=0)

    prompt = _prompt(reference_images=[str(ref_path)], duration_s=4)
    result = backend.render(prompt)

    assert result.status == "succeeded"
    assert client.models.calls[0]["config"]["duration_seconds"] == VEO_MAX_DURATION_S
    assert any("coerced" in warning for warning in result.raw["warnings"])


def test_render_failure_does_not_raise():
    client = FakeClient(raise_error=RuntimeError("Veo API exploded"))
    backend = VeoBackend(client=client, poll_interval_s=0)

    result = backend.render(_prompt())

    assert result.status == "failed"
    assert result.uri is None
    assert "Veo API exploded" in result.raw["error"]


def test_extend_from_is_ignored_but_noted_in_raw(tmp_path):
    client = FakeClient(done_after=1)
    backend = VeoBackend(client=client, out_dir=str(tmp_path), poll_interval_s=0)

    result = backend.render(_prompt(), extend_from="sc1-sh0")

    assert result.status == "succeeded"
    assert result.raw["extend_from"] == "sc1-sh0"
    assert any("extend_from" in warning for warning in result.raw["warnings"])
