"""CLI entry point: `python -m moviecrew "<concept>" [--out project.json] [--backend mock|anthropic]`."""

from __future__ import annotations

import argparse
import sys
from typing import Optional, Sequence

from .crew import MovieCrew
from .llm import LLMClient
from .mock import MockLLMClient


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
    args = parser.parse_args(argv)

    llm = _build_llm(args.backend)
    project = MovieCrew(llm).make(args.concept)

    _print_summary(project)

    if args.out:
        with open(args.out, "w") as f:
            f.write(project.to_json())
        print(f"  wrote {args.out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
