"""The orchestrator drives a backend it knows nothing about.

`MovieCrew.render()` used to build a Veo request itself and hand it to
whatever backend it was given, which meant every backend had to speak Veo
and the neutrality of `ShotIntent` stopped at the execution step. These
tests pin the property that replaced it: the orchestrator asks the backend
how to adapt a shot and how much of a take it can carry, and never decides
either itself.

The strongest test here is static — `crew.py` cannot import a vendor module
— because a behavioural test only proves the backends we thought to write
work, while the import check proves the coupling cannot come back.
"""

from __future__ import annotations

import ast
import pathlib
from dataclasses import dataclass, field
from typing import Optional, Sequence

import pytest

from moviecrew.backend import RenderResult, VideoBackend
from moviecrew.crew import MovieCrew
from moviecrew.generative import GenerativeVideoBackend
from moviecrew.mock import MockLLMClient
from moviecrew.render import (
    CostModel,
    FakeRenderClient,
    RenderCapabilities,
    ShotSpec,
)
from moviecrew.schema import (
    Bible,
    Project,
    RenderPlan,
    Scene,
    Shot,
    ShotIntent,
)
from moviecrew.video import VEO_MAX_CHAIN_SEGMENTS, StubVideoBackend, VeoPrompt


# ---------------------------------------------------------------------- #
# A backend with no relationship to Veo whatsoever                        #
# ---------------------------------------------------------------------- #


@dataclass
class CallSheet:
    """What a film unit is handed: no clamping, no caps, no vendor."""

    shot_id: str
    action: str
    seconds: float
    ratio: str
    references: list[str] = field(default_factory=list)


class FilmUnit(VideoBackend[CallSheet]):
    """A camera crew. Shoots exactly what it was asked for, and rolls for as
    long as the take runs — the honest opposite of a hosted model."""

    name = "film-unit"

    def __init__(self) -> None:
        self.rendered: list[CallSheet] = []
        self.runs: list[list[str]] = []

    def segment(self, chain):
        self.runs.append(list(chain))
        return super().segment(chain)

    def adapt(self, intent: ShotIntent, *, reference_images: Sequence[str] = ()):
        return CallSheet(
            shot_id=intent.shot_id,
            action=intent.description,
            seconds=intent.duration_s,
            ratio=intent.aspect_ratio,
            references=list(reference_images),
        )

    def render(self, request, *, extend_from=None, in_multishot_chain=False):
        self.rendered.append(request)
        return RenderResult(
            shot_id=request.shot_id,
            status="succeeded",
            backend=self.name,
            uri=f"reel/{request.shot_id}.mov",
        )


def _project(shots: list[Shot], *, chains=None, intents=None) -> Project:
    scene = Scene(id="sc1", slug="s", title="t", summary="s", shots=shots)
    order = [shot.id for shot in shots]
    return Project(
        title="t",
        logline="l",
        bible=Bible(style="s", palette="p", mood="m"),
        scenes=[scene],
        render_plan=RenderPlan(
            intents=intents or [],
            order=order,
            chains=chains if chains is not None else [[shot.id] for shot in shots],
        ),
    )


# ---------------------------------------------------------------------- #
# The orchestrator applies no backend's limits                            #
# ---------------------------------------------------------------------- #


def test_a_non_veo_backend_receives_the_unsnapped_duration():
    """11.5s is not a legal Veo clip. A camera crew does not care."""
    shot = Shot(id="s1", scene_id="sc1", description="d", duration_s=11.5)
    unit = FilmUnit()

    MovieCrew(MockLLMClient()).render(_project([shot]), unit)

    assert unit.rendered[0].seconds == 11.5


def test_a_non_veo_backend_receives_every_reference():
    """Veo's cap of three is Veo's, and is applied by Veo's adapter."""
    refs = [f"ref{n}.png" for n in range(7)]
    shot = Shot(
        id="s1", scene_id="sc1", description="d", duration_s=8, reference_image_ids=refs
    )
    unit = FilmUnit()

    MovieCrew(MockLLMClient()).render(_project([shot]), unit)

    assert unit.rendered[0].references == refs


def test_a_non_veo_backend_receives_a_ratio_veo_would_refuse():
    shot = Shot(id="s1", scene_id="sc1", description="d", duration_s=8)
    intent = ShotIntent(shot_id="s1", description="d", aspect_ratio="239:100")
    unit = FilmUnit()

    MovieCrew(MockLLMClient()).render(_project([shot], intents=[intent]), unit)

    assert unit.rendered[0].ratio == "239:100"


def test_a_long_take_is_not_split_for_a_backend_that_can_roll():
    """Veo splits at 21 segments; that number must not reach a backend that
    has no such limit."""
    length = VEO_MAX_CHAIN_SEGMENTS + 6
    shots = [
        Shot(id=f"s{i}", scene_id="sc1", description="d", duration_s=8)
        for i in range(length)
    ]
    chain = [shot.id for shot in shots]
    unit = FilmUnit()

    results = MovieCrew(MockLLMClient()).render(_project(shots, chains=[chain]), unit)

    assert unit.runs == [chain]
    assert len(results) == length


def test_the_veo_backend_still_splits_the_same_take():
    """The counterpart: the limit did not vanish, it moved to its owner."""
    length = VEO_MAX_CHAIN_SEGMENTS + 6
    shots = [
        Shot(id=f"s{i}", scene_id="sc1", description="d", duration_s=8)
        for i in range(length)
    ]
    stub = StubVideoBackend()

    results = MovieCrew(MockLLMClient()).render(
        _project(shots, chains=[[shot.id for shot in shots]]), stub
    )

    # The 22nd shot starts a fresh run, so it extends from nothing.
    assert results[VEO_MAX_CHAIN_SEGMENTS].raw["extend_from"] is None
    assert results[1].raw["extend_from"] == "s0"


def test_veo_s_adapter_still_applies_veo_s_limits():
    shot = Shot(
        id="s1",
        scene_id="sc1",
        description="d",
        duration_s=11.5,
        reference_image_ids=[f"r{n}.png" for n in range(7)],
    )
    stub = StubVideoBackend()

    results = MovieCrew(MockLLMClient()).render(_project([shot]), stub)

    assert results[0].raw["duration_s"] in (4, 6, 8)
    assert len(results[0].raw["reference_images"]) == 3


def test_adapting_never_mutates_the_intent():
    """Whatever a backend could not honour stays recoverable afterwards."""
    intent = ShotIntent(shot_id="s1", description="d", duration_s=11.5)
    shot = Shot(
        id="s1",
        scene_id="sc1",
        description="d",
        duration_s=11.5,
        reference_image_ids=[f"r{n}.png" for n in range(7)],
    )
    project = _project([shot], intents=[intent])

    MovieCrew(MockLLMClient()).render(project, StubVideoBackend())

    assert intent.duration_s == 11.5


def test_both_backends_render_one_plan_identically_in_shape():
    shots = [
        Shot(id=f"s{i}", scene_id="sc1", description="d", duration_s=8) for i in range(3)
    ]
    project = _project(shots)
    crew = MovieCrew(MockLLMClient())

    veo_results = crew.render(project, StubVideoBackend())
    unit_results = crew.render(project, FilmUnit())

    assert [r.shot_id for r in veo_results] == [r.shot_id for r in unit_results]


# ---------------------------------------------------------------------- #
# The coupling cannot come back                                           #
# ---------------------------------------------------------------------- #


def _imported_modules(path: str) -> set[str]:
    tree = ast.parse(pathlib.Path(path).read_text())
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
        elif isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
    return modules


def test_the_orchestrator_imports_no_vendor_module():
    """crew.py may import the neutral seam; it may not import an adapter."""
    modules = _imported_modules("moviecrew/crew.py")
    assert "backend" in modules
    assert "video" not in modules
    assert "generative" not in modules
    assert "render_openrouter" not in modules


@pytest.mark.parametrize("module", ["moviecrew/crew.py", "moviecrew/rules.py"])
def test_no_vendor_name_survives_in_generic_layers(module):
    """A stray `veo_` identifier is how the boundary erodes. Prose in a
    docstring may still cite Veo as an example; code may not name it."""
    tree = ast.parse(pathlib.Path(module).read_text())
    named = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
    } | {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.ClassDef))
    } | {
        node.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute)
    }
    offenders = sorted(n for n in named if "veo" in n.lower())
    assert not offenders, f"{module} still names a vendor in code: {offenders}"


def test_the_schema_names_no_vendor():
    import moviecrew.schema as schema

    assert not [name for name in vars(schema) if "veo" in name.lower()]


# ---------------------------------------------------------------------- #
# The generative bridge: one plan, a hosted async backend                 #
# ---------------------------------------------------------------------- #


def _capabilities(**overrides) -> RenderCapabilities:
    base = dict(
        max_duration_s=10,
        supported_resolutions=("480p", "720p"),
        supported_aspect_ratios=("16:9",),
        supports_video_reference=False,
        max_image_references=4,
        supports_audio=True,
        cost_model=CostModel(unit="usd_per_second", amount=0.1),
    )
    base.update(overrides)
    return RenderCapabilities(**base)


class _Client(FakeRenderClient):
    """A hosted backend whose capabilities the test dictates.

    FakeRenderClient already records every (spec, model) it was handed, so
    the specs a backend actually built are readable without a second log.
    """

    name = "hosted"

    def __init__(self, capabilities: RenderCapabilities, **kwargs) -> None:
        super().__init__(**kwargs)
        self._capabilities = capabilities

    def capabilities(self, model: Optional[str] = None) -> RenderCapabilities:
        return self._capabilities


def _specs(backend: GenerativeVideoBackend) -> list[ShotSpec]:
    return [spec for spec, _model in backend.client.submitted]


def _backend(capabilities=None, **kwargs) -> GenerativeVideoBackend:
    client = _Client(capabilities or _capabilities())
    return GenerativeVideoBackend(
        client, model="some/model", sleep=lambda _: None, **kwargs
    )


def test_the_generative_bridge_is_a_video_backend():
    assert isinstance(_backend(), VideoBackend)


def test_a_hosted_backend_renders_a_whole_plan(tmp_path):
    shots = [
        Shot(id=f"s{i}", scene_id="sc1", description="d", duration_s=6) for i in range(3)
    ]
    backend = _backend(out_dir=str(tmp_path))

    results = MovieCrew(MockLLMClient()).render(_project(shots), backend)

    assert [r.status for r in results] == ["succeeded"] * 3
    assert [r.backend for r in results] == ["hosted"] * 3


def test_duration_is_clamped_by_the_clients_own_answer(tmp_path):
    """30s asked for, 10s accepted — and the number came from the client."""
    shot = Shot(id="s1", scene_id="sc1", description="d", duration_s=30)
    backend = _backend(out_dir=str(tmp_path))

    MovieCrew(MockLLMClient()).render(_project([shot]), backend)

    assert _specs(backend)[0].duration_s == 10


def test_a_longer_limit_needs_no_code_change(tmp_path):
    shot = Shot(id="s1", scene_id="sc1", description="d", duration_s=30)
    backend = _backend(_capabilities(max_duration_s=30), out_dir=str(tmp_path))

    MovieCrew(MockLLMClient()).render(_project([shot]), backend)

    assert _specs(backend)[0].duration_s == 30


def test_references_are_capped_by_the_clients_own_answer(tmp_path):
    refs = [f"r{n}.png" for n in range(9)]
    shot = Shot(
        id="s1", scene_id="sc1", description="d", duration_s=6, reference_image_ids=refs
    )
    backend = _backend(out_dir=str(tmp_path))

    MovieCrew(MockLLMClient()).render(_project([shot]), backend)

    assert _specs(backend)[0].reference_images == refs[:4]


def test_a_model_with_no_extend_primitive_does_not_pretend_to_chain(tmp_path):
    """Silently rendering a take as unrelated clips is the failure this
    prevents: the chain is broken up where that is visible instead."""
    shots = [
        Shot(id=f"s{i}", scene_id="sc1", description="d", duration_s=6) for i in range(4)
    ]
    chain = [shot.id for shot in shots]
    backend = _backend(out_dir=str(tmp_path))

    assert backend.segment(chain) == [["s0"], ["s1"], ["s2"], ["s3"]]

    results = MovieCrew(MockLLMClient()).render(_project(shots, chains=[chain]), backend)
    assert all(spec.reference_video is None for spec in _specs(backend))
    assert len(results) == 4


def test_a_model_with_a_video_reference_keeps_the_take_whole(tmp_path):
    """Video input is half of it; the clip also has to reach the next
    render. Here a publisher supplies that half — without one this chain
    would be segmented instead, which `test_execution_semantics` covers."""
    shots = [
        Shot(id=f"s{i}", scene_id="sc1", description="d", duration_s=6) for i in range(3)
    ]
    chain = [shot.id for shot in shots]
    backend = _backend(
        _capabilities(supports_video_reference=True, max_video_references=1),
        out_dir=str(tmp_path),
        publish=lambda shot_id, url: f"https://cdn.example/{shot_id}.mp4",
    )

    MovieCrew(MockLLMClient()).render(_project(shots, chains=[chain]), backend)

    submitted = _specs(backend)
    assert submitted[0].reference_video is None
    assert submitted[1].reference_video == backend.produced_url_by_shot_id["s0"]
    assert submitted[2].reference_video == backend.produced_url_by_shot_id["s1"]


def test_a_broken_take_is_reported_not_papered_over(tmp_path):
    """If the predecessor produced nothing, the continuation is not a
    continuation — that has to surface.

    The publisher is what isolates this case: a backend that could not
    chain at all would be refused one step earlier, for a different reason.
    """
    backend = _backend(
        _capabilities(supports_video_reference=True),
        out_dir=str(tmp_path),
        publish=lambda shot_id, url: f"https://cdn.example/{shot_id}.mp4",
    )
    spec = backend.adapt(ShotIntent(shot_id="s2", description="d"))

    result = backend.render(spec, extend_from="s1", in_multishot_chain=True)

    assert result.status == "failed"
    assert "no rendered output for predecessor shot 's1'" in result.raw["error"]


def test_the_backend_reports_the_client_it_actually_used(tmp_path):
    """A take recorded against "generative" would say nothing useful."""
    assert _backend(out_dir=str(tmp_path)).name == "hosted"


def test_a_failed_render_becomes_a_failed_result(tmp_path):
    client = _Client(_capabilities(), fail_with="out of credit")
    backend = GenerativeVideoBackend(
        client, model="m", out_dir=str(tmp_path), sleep=lambda _: None
    )
    shot = Shot(id="s1", scene_id="sc1", description="d", duration_s=6)

    results = MovieCrew(MockLLMClient()).render(_project([shot]), backend)

    assert results[0].status == "failed"
    assert "credit" in results[0].raw["error"]


def test_polling_continues_until_the_job_is_terminal(tmp_path):
    client = _Client(_capabilities(), pending_polls=3)
    backend = GenerativeVideoBackend(
        client, model="m", out_dir=str(tmp_path), sleep=lambda _: None
    )
    shot = Shot(id="s1", scene_id="sc1", description="d", duration_s=6)

    results = MovieCrew(MockLLMClient()).render(_project([shot]), backend)

    assert results[0].status == "succeeded"


def test_a_stalled_render_times_out_rather_than_hanging(tmp_path):
    client = _Client(_capabilities(), pending_polls=10_000)
    clock = iter([0.0, 1.0, 2.0, 3.0, 4.0, 5_000.0, 10_000.0])
    backend = GenerativeVideoBackend(
        client,
        model="m",
        out_dir=str(tmp_path),
        sleep=lambda _: None,
        monotonic=lambda: next(clock),
        timeout_s=60,
    )
    shot = Shot(id="s1", scene_id="sc1", description="d", duration_s=6)

    results = MovieCrew(MockLLMClient()).render(_project([shot]), backend)

    assert results[0].status == "failed"
    assert "did not finish" in results[0].raw["error"]


def test_the_veo_prompt_type_never_reaches_a_generative_backend(tmp_path):
    """Each backend's adapt() output is the only thing its render() sees."""
    backend = _backend(out_dir=str(tmp_path))
    spec = backend.adapt(ShotIntent(shot_id="s1", description="d"))
    assert isinstance(spec, ShotSpec)
    assert not isinstance(spec, VeoPrompt)


# ---------------------------------------------------------------------- #
# Choosing a backend at the command line                                  #
# ---------------------------------------------------------------------- #


def _advertised_video_backends() -> list[str]:
    """The --video-backend choices the parser actually offers."""
    tree = ast.parse(pathlib.Path("moviecrew/cli.py").read_text())
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        args = [a for a in node.args if isinstance(a, ast.Constant)]
        if not any(a.value == "--video-backend" for a in args):
            continue
        for keyword in node.keywords:
            if keyword.arg == "choices":
                return [elt.value for elt in keyword.value.elts]
    raise AssertionError("no --video-backend argument found in cli.py")


def test_the_stub_backend_builds_with_no_credentials():
    from moviecrew.cli import _build_video_backend

    backend = _build_video_backend(
        "stub", model="m", out_dir="renders", resolution="720p"
    )
    assert isinstance(backend, VideoBackend)


def test_every_advertised_choice_is_actually_handled():
    """A choice the parser offers and the factory rejects is a dead option
    the user only discovers by running a whole pipeline first."""
    from moviecrew.cli import _build_video_backend

    for choice in _advertised_video_backends():
        try:
            _build_video_backend(
                choice, model="m", out_dir="renders", resolution="720p"
            )
        except Exception as exc:  # missing SDK or key is fine; unknown is not
            assert "unknown video backend" not in str(exc), choice


def test_an_unknown_backend_choice_is_refused():
    from moviecrew.cli import _build_video_backend

    with pytest.raises(ValueError, match="unknown video backend"):
        _build_video_backend("holodeck", model="m", out_dir="r", resolution="720p")


def test_the_openrouter_choice_names_the_missing_key(monkeypatch):
    """A backend that cannot be built should say what is missing, not fail
    somewhere deep in a render."""
    from moviecrew.cli import _build_video_backend
    from moviecrew.render_openrouter import API_KEY_ENV

    monkeypatch.delenv(API_KEY_ENV, raising=False)
    with pytest.raises(Exception, match=API_KEY_ENV):
        _build_video_backend(
            "openrouter", model="m", out_dir="r", resolution="720p"
        )
