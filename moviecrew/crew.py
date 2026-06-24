"""The MovieCrew orchestrator: concept in, Project out.

Runs the seven role agents in a fixed pipeline (director -> writer ->
designer -> cinematographer -> prompter -> continuity -> editor),
accumulating their output into the schema's dataclasses. Deterministic
guardrails from moviecrew.rules run between the agent calls so the Bible
stays the source of truth for reference images, and so durations/order are
computed rather than trusted from the LLM.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Optional

from .agents import (
    CinematographerAgent,
    ContinuityAgent,
    DesignerAgent,
    DirectorAgent,
    EditorAgent,
    PrompterAgent,
    WriterAgent,
)
from .llm import LLMClient
from .rules import assign_reference_images, normalize_chains, veo_constraint_flags
from .schema import (
    Bible,
    Character,
    ContinuityFlag,
    Location,
    Project,
    RenderPlan,
    Scene,
    Shot,
    VeoPrompt,
)
from .video import RenderResult, VideoBackend


class MovieCrew:
    """Coordinates the seven role agents into a finished Project."""

    def __init__(self, llm: LLMClient, models: Optional[dict[str, str]] = None) -> None:
        self.llm = llm
        # Reserved for a future per-task model override (e.g. a custom
        # AnthropicLLMClient routing table); unused by the offline pipeline.
        self.models = models or {}

        self.director = DirectorAgent(llm)
        self.writer = WriterAgent(llm)
        self.designer = DesignerAgent(llm)
        self.cinematographer = CinematographerAgent(llm)
        self.prompter = PrompterAgent(llm)
        self.continuity = ContinuityAgent(llm)
        self.editor = EditorAgent(llm)

    def make(self, concept: str) -> Project:
        director_out = self.director.run(concept=concept)
        title = director_out["title"]
        logline = director_out["logline"]
        outline = director_out["outline"]

        writer_out = self.writer.run(title=title, logline=logline, outline=outline)
        raw_scenes = writer_out["scenes"]

        designer_out = self.designer.run(title=title, logline=logline, scenes=raw_scenes)
        bible = Bible(
            style=designer_out["style"],
            palette=designer_out["palette"],
            mood=designer_out["mood"],
            characters=[Character(**c) for c in designer_out["characters"]],
            locations=[Location(**l) for l in designer_out["locations"]],
        )

        scenes: list[Scene] = []
        all_shots: list[Shot] = []
        for raw_scene in raw_scenes:
            scene = Scene(**raw_scene)

            cine_out = self.cinematographer.run(scene=raw_scene)
            shots = [Shot(**s) for s in cine_out["shots"] if s["scene_id"] == scene.id]
            for shot in shots:
                assign_reference_images(shot, scene, bible)

            scene.shots = shots
            scenes.append(scene)
            all_shots.extend(shots)

        prompts: list[VeoPrompt] = []
        flags: list[ContinuityFlag] = []
        for shot in all_shots:
            prompter_out = self.prompter.run(shot=asdict(shot))
            raw_prompts = [p for p in prompter_out["prompts"] if p["shot_id"] == shot.id]
            for raw_prompt in raw_prompts:
                prompt_text = raw_prompt["prompt"]
                prompts.append(
                    VeoPrompt(
                        shot_id=shot.id,
                        prompt=prompt_text,
                        negative_prompt=raw_prompt.get("negative_prompt", ""),
                        duration_s=shot.duration_s,
                        aspect_ratio="16:9",
                        reference_images=list(shot.reference_image_ids),
                    )
                )
                flags.extend(veo_constraint_flags(prompt_text, shot))

        continuity_out = self.continuity.run(
            scenes=[asdict(scene) for scene in scenes],
            prompts=[asdict(prompt) for prompt in prompts],
        )
        flags.extend(ContinuityFlag(**f) for f in continuity_out["flags"])

        for scene in scenes:
            if not scene.character_ids:
                continue
            for shot in scene.shots:
                if not shot.reference_image_ids:
                    flags.append(
                        ContinuityFlag(
                            target=shot.id,
                            kind="warning",
                            message=(
                                f"Shot {shot.id} has characters in its scene but no "
                                "reference images were assigned."
                            ),
                        )
                    )

        deduped_flags: dict[tuple[str, str, str], ContinuityFlag] = {}
        for flag in flags:
            deduped_flags.setdefault((flag.kind, flag.target, flag.message), flag)
        flags = list(deduped_flags.values())

        editor_out = self.editor.run(shot_ids=[shot.id for shot in all_shots])
        order = editor_out["order"]
        chains = normalize_chains(all_shots, order, editor_out.get("chains", []))

        est_duration_s = sum(shot.duration_s for shot in all_shots)

        render_plan = RenderPlan(
            prompts=prompts,
            flags=flags,
            order=order,
            chains=chains,
            est_duration_s=est_duration_s,
        )

        return Project(
            title=title,
            logline=logline,
            bible=bible,
            outline=outline,
            scenes=scenes,
            render_plan=render_plan,
        )

    def render(self, project: Project, backend: VideoBackend) -> list[RenderResult]:
        """Render every prompt in project.render_plan through `backend`, in
        render_plan.order. Pure orchestration: makes no network calls itself.

        Chain-aware: a shot that continues a Veo extend-chain is rendered
        with extend_from set to its predecessor's shot id within that chain;
        a chain's first shot (or a standalone shot) gets extend_from=None.
        Every shot in a chain of 2+ (its head or one of its extensions) is
        passed in_multishot_chain=True so the backend can keep it at a
        resolution Veo allows to extend.
        """
        render_plan = project.render_plan
        if render_plan is None:
            return []

        extend_from_by_shot_id: dict[str, Optional[str]] = {}
        in_multishot_chain_by_shot_id: dict[str, bool] = {}
        for chain in render_plan.chains:
            in_chain = len(chain) >= 2
            for shot_id in chain:
                in_multishot_chain_by_shot_id[shot_id] = in_chain
            for predecessor, shot_id in zip(chain, chain[1:]):
                extend_from_by_shot_id[shot_id] = predecessor

        prompts_by_shot_id = {prompt.shot_id: prompt for prompt in render_plan.prompts}
        results: list[RenderResult] = []
        for shot_id in render_plan.order:
            prompt = prompts_by_shot_id.get(shot_id)
            if prompt is None:
                continue
            results.append(
                backend.render(
                    prompt,
                    extend_from=extend_from_by_shot_id.get(shot_id),
                    in_multishot_chain=in_multishot_chain_by_shot_id.get(shot_id, False),
                )
            )
        return results
