"""CLI entry point: `python -m moviecrew "<concept>" [--out project.json] [--backend mock|openrouter|anthropic]`."""

from __future__ import annotations

import argparse
import sys
from typing import Optional, Sequence

from .agents import DETAIL_LEVELS
from .assembly import assemble_film
from .backend import RenderResult, VideoBackend
from .crew import MovieCrew
from .llm import LLMClient
from .mock import MockLLMClient
from .reference import FileReferenceImageProvider, ReferenceImageProvider
from .video import StubVideoBackend, VeoBackend

# OpenRouter's Seedance id; override with --render-model.
DEFAULT_GENERATIVE_MODEL = "bytedance/seedance-1-pro"


def _build_llm(backend: str) -> LLMClient:
    if backend == "mock":
        return MockLLMClient()
    if backend == "openrouter":
        from .llm_openrouter import OpenRouterLLMClient

        return OpenRouterLLMClient()
    if backend == "anthropic":
        from .llm import AnthropicLLMClient

        return AnthropicLLMClient()
    raise ValueError(f"unknown backend: {backend}")


def _asset_publisher(out_dir: str):
    """The `publish=` a `GenerativeVideoBackend` needs to keep a chain
    whole, or None when nothing configured here could actually deliver one.

    `build_asset_store` reads the same $MOVIECREW_S3_* variables the portal
    reads (and the settings screen writes) — R2 credentials opt into a real
    bucket, and no credentials means the local fallback, whose URLs are
    never fetchable by an external provider with no server address to give
    it. `store.serves_public_urls` is exactly that check, so a chain stays
    correctly disabled with nothing configured, and starts working the
    moment a bucket does — no change here when that happens.
    """
    from .assets import build_asset_store

    store = build_asset_store(local_root=out_dir)
    if not store.serves_public_urls:
        return None

    def publish(shot_id: str, local_path: str) -> str:
        asset = store.put_reachable(local_path, f"renders/{shot_id}.mp4")
        return asset.url

    return publish


def _build_video_backend(
    choice: str, *, model: str, out_dir: str, resolution: str
) -> VideoBackend:
    """Pick an execution backend. Each one adapts a shot in its own terms;
    nothing above this line knows which was chosen.
    """
    if choice == "stub":
        return StubVideoBackend()
    if choice == "veo":
        return VeoBackend(out_dir=out_dir)
    if choice == "openrouter":
        from .generative import GenerativeVideoBackend
        from .render_openrouter import OpenRouterRenderClient

        return GenerativeVideoBackend(
            OpenRouterRenderClient(),
            model=model,
            out_dir=out_dir,
            resolution=resolution,
            publish=_asset_publisher(out_dir),
        )
    raise ValueError(f"unknown video backend: {choice}")


def _print_summary(project) -> None:
    scene_count = len(project.scenes)
    shot_count = sum(len(scene.shots) for scene in project.scenes)
    est_duration_s = project.render_plan.est_duration_s if project.render_plan else 0

    print(f"{project.title}")
    print(f"  logline: {project.logline}")
    print(f"  scenes: {scene_count}  shots: {shot_count}  est. duration: {est_duration_s}s")

    flags = project.render_plan.flags if project.render_plan else []
    if flags:
        print(f"  flags ({len(flags)}):")
        for flag in flags:
            print(f"    [{flag.kind}] {flag.target}: {flag.message}")


def _print_render_results(results: list[RenderResult]) -> None:
    print(f"  render ({len(results)} shots):")
    for result in results:
        uri = f" -> {result.uri}" if result.uri else ""
        print(f"    [{result.backend}] {result.shot_id}: {result.status}{uri}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="moviecrew")
    parser.add_argument("concept", help="One-line movie concept")
    parser.add_argument("--out", help="Write the resulting Project as JSON to this path")
    parser.add_argument(
        "--backend",
        choices=["mock", "openrouter", "anthropic"],
        default="mock",
        help=(
            "LLM backend to use (default: mock, runs fully offline). "
            "openrouter runs the whole crew on Sonnet 5 through one key."
        ),
    )
    parser.add_argument(
        "--render",
        action="store_true",
        help="Render the resulting shots (default: stub backend, runs fully offline)",
    )
    parser.add_argument(
        "--video-backend",
        choices=["stub", "veo", "openrouter"],
        default="stub",
        help=(
            "Video backend used by --render (default: stub, runs fully offline). "
            "veo calls the real Veo API and requires a GEMINI_API_KEY/GOOGLE_API_KEY "
            "and the google-genai extra. openrouter renders through a hosted model "
            "(see --render-model) and requires an OPENROUTER_API_KEY. Both spend money."
        ),
    )
    parser.add_argument(
        "--render-model",
        metavar="ID",
        default=DEFAULT_GENERATIVE_MODEL,
        help=(
            f"Model id for --video-backend openrouter (default: {DEFAULT_GENERATIVE_MODEL})"
        ),
    )
    parser.add_argument(
        "--render-dir",
        metavar="DIR",
        default="renders",
        help="Directory rendered clips are written to (default: renders)",
    )
    parser.add_argument(
        "--resolution",
        default="720p",
        help="Render resolution for backends that accept one (default: 720p)",
    )
    parser.add_argument(
        "--assemble",
        metavar="OUT.mp4",
        help=(
            "After --render, concatenate each chain's final clip into this file via "
            "ffmpeg (requires ffmpeg on PATH)"
        ),
    )
    parser.add_argument(
        "--reference-dir",
        metavar="DIR",
        help=(
            "Directory of hand-made character stills (DIR/<character_id>.png); enables "
            "consistency anchoring on chain-head shots for characters with a real still "
            "there. Default: no reference provider, so nothing anchors."
        ),
    )
    parser.add_argument(
        "--detail",
        choices=sorted(DETAIL_LEVELS),
        default="cinematic",
        help="Shot-prompt density: lean (short), cinematic (default), or maximal (dense)",
    )
    parser.add_argument(
        "--bible",
        metavar="DIR",
        help=(
            "Load a visual Bible library from DIR (assets-first mode): the writer "
            "crafts scenes for the provided cast and world, and the designer only "
            "fills any gaps. Stills in DIR/stills/ are used as reference images."
        ),
    )
    parser.add_argument(
        "--save-bible",
        metavar="DIR",
        help=(
            "After the run, persist the generated (or merged) Bible as a reusable "
            "library in DIR for future --bible use (the bridge between story-first "
            "and assets-first modes)."
        ),
    )
    args = parser.parse_args(argv)

    llm = _build_llm(args.backend)
    reference_provider: Optional[ReferenceImageProvider] = (
        FileReferenceImageProvider(args.reference_dir) if args.reference_dir else None
    )
    crew = MovieCrew(llm, reference_provider=reference_provider, prompt_detail=args.detail)

    input_bible = None
    if args.bible:
        from .library import load_bible

        input_bible = load_bible(args.bible)

    project = crew.make(args.concept, bible=input_bible)

    _print_summary(project)

    if args.render:
        video_backend = _build_video_backend(
            args.video_backend,
            model=args.render_model,
            out_dir=args.render_dir,
            resolution=args.resolution,
        )
        results = crew.render(project, video_backend)
        _print_render_results(results)

        if args.assemble:
            # Which clips carry the footage depends on how this backend split
            # the chains and on what its clips contain, so assembly is told
            # what was actually executed rather than left to guess.
            assembled = assemble_film(
                project,
                results,
                args.assemble,
                runs=crew.plan_execution(project, video_backend),
            )
            if assembled:
                print(f"  assembled -> {assembled}")
            else:
                print("  assembled -> skipped (no usable clips)")

    if args.save_bible:
        from .library import save_bible

        save_bible(project.bible, args.save_bible)
        print(f"  saved Bible -> {args.save_bible}/bible.json")

    if args.out:
        with open(args.out, "w") as f:
            f.write(project.to_json())
        print(f"  wrote {args.out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
