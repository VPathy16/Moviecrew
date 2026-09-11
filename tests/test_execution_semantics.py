"""What a backend produced, and what that means for the cut.

Every test here defends against a silent wrong answer rather than a crash.
An editorial chain, the runs a backend split it into, and what one of its
clips contains are three different things, and collapsing them loses
footage or money without raising anything.

Regression tests for the #23 review:
  1. assembly followed canonical chains, not execution runs
  2. max_image_references=0 meant both "no cap" and "no references"
  3. a chained clip's URL may not be one the provider can read
  4. a billed generation whose download failed reported success
"""

from __future__ import annotations

import pytest

from moviecrew.assembly import assemble_film
from moviecrew.backend import ChainOutput, ExecutionRun
from moviecrew.crew import MovieCrew
from moviecrew.generative import GenerativeVideoBackend
from moviecrew.mock import MockLLMClient
from moviecrew.render import (
    FakeRenderClient,
    JobStatus,
    RenderCapabilities,
    RenderJob,
    ShotSpec,
)
from moviecrew.render_openrouter import OpenRouterRenderClient
from moviecrew.schema import Bible, Project, RenderPlan, Scene, Shot
from moviecrew.video import StubVideoBackend


class FakeRun:
    def __init__(self):
        self.calls: list[list[str]] = []

    def __call__(self, command, **kwargs):
        self.calls.append(list(command))


def _clips_in(command: list[str]) -> list[str]:
    return [command[i + 1] for i, arg in enumerate(command) if arg == "-i"]


def _project(shots: list[Shot], chains) -> Project:
    scene = Scene(id="sc1", slug="s", title="t", summary="s", shots=shots)
    return Project(
        title="t",
        logline="l",
        bible=Bible(style="s", palette="p", mood="m"),
        scenes=[scene],
        render_plan=RenderPlan(
            order=[shot.id for shot in shots], chains=chains
        ),
    )


def _shots(n: int) -> list[Shot]:
    return [
        Shot(id=f"s{i}", scene_id="sc1", description="d", duration_s=6)
        for i in range(n)
    ]


# ---------------------------------------------------------------------- #
# 1. Assembly follows execution, not the editorial chain                  #
# ---------------------------------------------------------------------- #


def _capabilities(**overrides) -> RenderCapabilities:
    base = dict(
        max_duration_s=10,
        supported_resolutions=("480p", "720p"),
        supported_aspect_ratios=("16:9",),
        supports_video_reference=False,
        max_image_references=4,
        supports_audio=True,
    )
    base.update(overrides)
    return RenderCapabilities(**base)


class _Client(FakeRenderClient):
    name = "hosted"

    def __init__(self, capabilities: RenderCapabilities, **kwargs) -> None:
        super().__init__(**kwargs)
        self._capabilities = capabilities

    def capabilities(self, model=None) -> RenderCapabilities:
        return self._capabilities


def _hosted(capabilities=None, **kwargs) -> GenerativeVideoBackend:
    return GenerativeVideoBackend(
        _Client(capabilities or _capabilities()),
        model="m",
        sleep=lambda _: None,
        **kwargs,
    )


def test_a_chain_rendered_per_shot_keeps_every_shot_in_the_cut(tmp_path):
    """The bug this file exists for: a four-shot chain on a backend that
    cannot continue a take was assembled down to one clip, and the other
    three renders — paid for, and on disk — never reached the film."""
    shots = _shots(4)
    chain = [shot.id for shot in shots]
    project = _project(shots, [chain])
    backend = _hosted(out_dir=str(tmp_path))
    crew = MovieCrew(MockLLMClient())

    results = crew.render(project, backend)
    runs = crew.plan_execution(project, backend)
    ffmpeg = FakeRun()

    assemble_film(project, results, "film.mp4", runs=runs, run=ffmpeg)

    assert len(_clips_in(ffmpeg.calls[0])) == 4


def test_a_cumulative_chain_still_uses_only_its_final_clip(tmp_path):
    """The counterpart: concatenating Veo's earlier clips would replay the
    take, because each one is already contained in the next."""
    shots = _shots(4)
    project = _project(shots, [[shot.id for shot in shots]])
    backend = StubVideoBackend()
    crew = MovieCrew(MockLLMClient())

    results = crew.render(project, backend)
    for result in results:  # the stub renders nothing, so stand clips in
        result.status = "succeeded"
        result.uri = f"renders/{result.shot_id}.mp4"

    ffmpeg = FakeRun()
    assemble_film(
        project,
        results,
        "film.mp4",
        runs=crew.plan_execution(project, backend),
        run=ffmpeg,
    )

    assert _clips_in(ffmpeg.calls[0]) == ["renders/s3.mp4"]


def test_a_long_cumulative_take_contributes_one_clip_per_run():
    """Split at 21, a 27-shot take is two runs — so two clips, not one and
    not 27."""
    from moviecrew.video import VEO_MAX_CHAIN_SEGMENTS

    shots = _shots(VEO_MAX_CHAIN_SEGMENTS + 6)
    project = _project(shots, [[shot.id for shot in shots]])
    crew = MovieCrew(MockLLMClient())
    backend = StubVideoBackend()

    runs = crew.plan_execution(project, backend)
    results = crew.render(project, backend)
    for result in results:
        result.status = "succeeded"
        result.uri = f"renders/{result.shot_id}.mp4"

    ffmpeg = FakeRun()
    assemble_film(project, results, "film.mp4", runs=runs, run=ffmpeg)

    assert len(runs) == 2
    assert _clips_in(ffmpeg.calls[0]) == [
        f"renders/s{VEO_MAX_CHAIN_SEGMENTS - 1}.mp4",
        f"renders/s{len(shots) - 1}.mp4",
    ]


def test_execution_runs_record_the_chain_they_came_from():
    shots = _shots(3)
    chain = [shot.id for shot in shots]
    project = _project(shots, [chain])

    runs = MovieCrew(MockLLMClient()).plan_execution(project, _hosted())

    assert [run.chain for run in runs] == [tuple(chain)] * 3
    assert [run.shot_ids for run in runs] == [("s0",), ("s1",), ("s2",)]


def test_clip_shot_ids_reads_the_semantics():
    run = ExecutionRun(chain=("a", "b"), shot_ids=("a", "b"))
    assert run.clip_shot_ids == ["a", "b"]

    cumulative = ExecutionRun(
        chain=("a", "b"), shot_ids=("a", "b"), output=ChainOutput.CUMULATIVE
    )
    assert cumulative.clip_shot_ids == ["b"]


def test_an_empty_run_contributes_nothing():
    assert ExecutionRun(chain=(), shot_ids=()).clip_shot_ids == []


def test_omitting_runs_announces_the_assumption_it_is_making(capsys):
    """The old behaviour is still the fallback, but it is no longer silent:
    a caller that does not say how the work was executed is told what was
    assumed on its behalf."""
    shots = _shots(3)
    project = _project(shots, [[shot.id for shot in shots]])
    results = MovieCrew(MockLLMClient()).render(project, StubVideoBackend())
    for result in results:
        result.status = "succeeded"
        result.uri = f"renders/{result.shot_id}.mp4"

    assemble_film(project, results, "film.mp4", run=FakeRun())

    assert "cumulative" in capsys.readouterr().err


def test_a_backend_declares_what_its_clips_contain():
    assert StubVideoBackend().chain_output is ChainOutput.CUMULATIVE
    assert _hosted().chain_output is ChainOutput.PER_SHOT
    assert (
        _hosted(_capabilities(supports_video_reference=True)).chain_output
        is ChainOutput.PER_SHOT
    ), "conditioning on a reference video returns the new shot, not the take"


# ---------------------------------------------------------------------- #
# 2. An unstated reference cap is not a cap of zero                       #
# ---------------------------------------------------------------------- #


def _catalogue(entry: dict) -> OpenRouterRenderClient:
    def transport(method, url, headers, body):
        return {"data": [entry]}

    return OpenRouterRenderClient(api_key="k", transport=transport)


def test_a_silent_catalogue_means_unknown_not_zero():
    client = _catalogue({"id": "vendor/model"})
    assert client.capabilities("vendor/model").max_image_references is None


def test_a_silent_catalogue_keeps_every_reference():
    """The regression: routing through the bridge used to delete every
    character reference for any model whose catalogue omits the field, and
    still bill for the render."""
    client = _catalogue({"id": "vendor/model"})
    refs = [f"r{n}.png" for n in range(6)]

    body = client.build_request(
        ShotSpec(shot_id="s1", prompt="p", reference_images=list(refs)),
        model="vendor/model",
    )

    assert body["provider"]["options"]["image_urls"] == refs


def test_the_bridge_agrees_with_the_client_on_a_silent_catalogue():
    from moviecrew.schema import ShotIntent

    capabilities = RenderCapabilities(max_duration_s=10)
    assert capabilities.max_image_references is None

    refs = [f"r{n}.png" for n in range(6)]
    spec = _hosted(capabilities).adapt(
        ShotIntent(shot_id="s1", description="d"), reference_images=refs
    )

    assert spec.reference_images == refs


def test_a_stated_cap_of_zero_really_does_drop_them():
    """The other half: a model that says it takes no images gets none."""
    from moviecrew.schema import ShotIntent

    spec = _hosted(_capabilities(max_image_references=0)).adapt(
        ShotIntent(shot_id="s1", description="d"), reference_images=["a.png"]
    )
    assert spec.reference_images == []


def test_a_stated_cap_of_zero_sends_no_image_urls():
    client = _catalogue({"id": "vendor/model", "max_image_references": 0})
    body = client.build_request(
        ShotSpec(shot_id="s1", prompt="p", reference_images=["a.png"]),
        model="vendor/model",
    )
    assert "image_urls" not in body.get("provider", {}).get("options", {})


def test_a_stated_cap_is_honoured():
    client = _catalogue({"id": "vendor/model", "max_image_references": 2})
    body = client.build_request(
        ShotSpec(shot_id="s1", prompt="p", reference_images=["a.png", "b.png", "c.png"]),
        model="vendor/model",
    )
    assert body["provider"]["options"]["image_urls"] == ["a.png", "b.png"]


@pytest.mark.parametrize(
    "cap,expected",
    [(None, 3), (0, 0), (1, 1), (5, 3)],
)
def test_cap_image_references_is_the_one_rule(cap, expected):
    capabilities = RenderCapabilities(max_duration_s=8, max_image_references=cap)
    assert len(capabilities.cap_image_references(["a", "b", "c"])) == expected


# ---------------------------------------------------------------------- #
# 3. A chained clip must be one the provider can actually read            #
# ---------------------------------------------------------------------- #


def test_chaining_without_a_publisher_says_the_url_may_be_unreachable(tmp_path):
    """OpenRouter results sit behind the same API auth as everything else —
    fetch() sends a Bearer token for exactly that reason — and a URL passed
    onward in provider.options carries no such header."""
    shots = _shots(2)
    project = _project(shots, [[shot.id for shot in shots]])
    backend = _hosted(
        _capabilities(supports_video_reference=True), out_dir=str(tmp_path)
    )

    results = MovieCrew(MockLLMClient()).render(project, backend)

    assert any("publish=" in w for w in results[1].raw["warnings"])


def test_a_publisher_rehosts_the_clip_and_the_warning_goes(tmp_path):
    published: list[tuple[str, str]] = []

    def publish(shot_id: str, url: str) -> str:
        published.append((shot_id, url))
        return f"https://cdn.example/{shot_id}.mp4"

    shots = _shots(2)
    project = _project(shots, [[shot.id for shot in shots]])
    backend = _hosted(
        _capabilities(supports_video_reference=True),
        out_dir=str(tmp_path),
        publish=publish,
    )

    results = MovieCrew(MockLLMClient()).render(project, backend)

    assert backend.produced_url_by_shot_id["s0"] == "https://cdn.example/s0.mp4"
    assert results[1].raw["reference_video"] == "https://cdn.example/s0.mp4"
    assert not any("publish=" in w for w in results[1].raw["warnings"])
    assert [shot_id for shot_id, _ in published] == ["s0", "s1"]


# ---------------------------------------------------------------------- #
# 4. A billed render with no clip is not a success                        #
# ---------------------------------------------------------------------- #


class _NoDownloadClient(_Client):
    """Generates fine, and the download fails — which `fetch` is documented
    to signal by returning None."""

    def fetch(self, job: RenderJob, out_path: str):
        return None

    def submit(self, spec: ShotSpec, *, model: str) -> RenderJob:
        job = super().submit(spec, model=model)
        job.cost = 0.42
        job.video_url = "https://openrouter.ai/results/abc.mp4"
        return job


def test_a_failed_download_is_not_reported_as_a_success(tmp_path):
    backend = GenerativeVideoBackend(
        _NoDownloadClient(_capabilities()),
        model="m",
        out_dir=str(tmp_path),
        sleep=lambda _: None,
    )
    shot = Shot(id="s1", scene_id="sc1", description="d", duration_s=6)
    project = _project([shot], [["s1"]])

    results = MovieCrew(MockLLMClient()).render(project, backend)

    assert results[0].status == "failed"
    assert results[0].uri is None
    assert "could not be downloaded" in results[0].raw["error"]


def test_a_failed_download_still_records_what_it_cost(tmp_path):
    """The money was spent whether or not the file arrived; losing that
    makes the spend unauditable and the render unretryable."""
    backend = GenerativeVideoBackend(
        _NoDownloadClient(_capabilities()),
        model="m",
        out_dir=str(tmp_path),
        sleep=lambda _: None,
    )
    shot = Shot(id="s1", scene_id="sc1", description="d", duration_s=6)

    results = MovieCrew(MockLLMClient()).render(_project([shot], [["s1"]]), backend)

    assert results[0].raw["cost"] == 0.42
    assert results[0].raw["video_url"] == "https://openrouter.ai/results/abc.mp4"
    assert results[0].raw["status"] == JobStatus.SUCCEEDED.value


def test_a_clipless_render_never_reaches_the_cut(tmp_path):
    backend = GenerativeVideoBackend(
        _NoDownloadClient(_capabilities()),
        model="m",
        out_dir=str(tmp_path),
        sleep=lambda _: None,
    )
    shots = _shots(2)
    project = _project(shots, [[shot.id] for shot in shots])
    crew = MovieCrew(MockLLMClient())

    results = crew.render(project, backend)
    out = assemble_film(
        project,
        results,
        "film.mp4",
        runs=crew.plan_execution(project, backend),
        run=FakeRun(),
    )

    assert out is None
