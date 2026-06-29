"""CLI entry point: `python -m moviecrew "<concept>" [--out project.json] [--backend mock|anthropic]`."""

from __future__ import annotations

import argparse
import sys
from typing import Optional, Sequence

from .assembly import assemble_film
from .crew import MovieCrew
from .llm import LLMClient
from .mock import MockLLMClient
from .reference import FileReferenceImageProvider, ReferenceImageProvider
from .video import RenderResult, StubVideoBackend, VeoBackend, VideoBackend


def _build_llm(backend: str) -> LLMClient:
    if backend == "mock":
        return MockLLMClient()
    if backend == "anthropic":
        from .llm import AnthropicLLMClient

        return AnthropicLLMClient()
    raise ValueError(f"unknown backend: {backend}")


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
        choices=["mock", "anthropic"],
        default="mock",
        help="LLM backend to use (default: mock, runs fully offline)",
    )
    parser.add_argument(
        "--render",
        action="store_true",
        help="Render the resulting shots (default: stub backend, runs fully offline)",
    )
    parser.add_argument(
        "--video-backend",
        choices=["stub", "veo"],
        default="stub",
        help=(
            "Video backend used by --render (default: stub, runs fully offline; "
            "veo calls the real Veo API and requires a GEMINI_API_KEY/GOOGLE_API_KEY "
            "and the google-genai extra)"
        ),
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
    args = parser.parse_args(argv)

    llm = _build_llm(args.backend)
    reference_provider: Optional[ReferenceImageProvider] = (
        FileReferenceImageProvider(args.reference_dir) if args.reference_dir else None
    )
    crew = MovieCrew(llm, reference_provider=reference_provider)
    project = crew.make(args.concept)

    _print_summary(project)

    if args.render:
        video_backend: VideoBackend = StubVideoBackend() if args.video_backend == "stub" else VeoBackend()
        results = crew.render(project, video_backend)
        _print_render_results(results)

        if args.assemble:
            assembled = assemble_film(project, results, args.assemble)
            if assembled:
                print(f"  assembled -> {assembled}")
            else:
                print("  assembled -> skipped (no usable clips)")

    if args.out:
        with open(args.out, "w") as f:
            f.write(project.to_json())
        print(f"  wrote {args.out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
