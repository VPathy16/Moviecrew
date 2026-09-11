"""The MovieCrew orchestrator: concept in, Project out.

Runs the seven role agents in a fixed pipeline (director -> writer ->
designer -> cinematographer -> editor -> prompter -> continuity),
accumulating their output into the schema's dataclasses. Deterministic
guardrails run between the agent calls: moviecrew.rules.normalize_chains
computes render order/chains from the editor's output before anything
depends on them, moviecrew.rules.select_anchors then attaches reference
stills (from moviecrew.reference) to each chain's head shot for cross-cut
character consistency, and prompts are built from the now-final shot
fields — so order, chains, durations, and reference images are all
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
from .reference import NullReferenceImageProvider, ReferenceImageProvider, populate_reference_stills
from .production import UnknownShot, resolve_shot
from .rules import (
    normalize_chains,
    normalize_order,
    select_anchors,
    veo_constraint_flags,
)
from .schema import (
    DEFAULT_ASPECT_RATIO,
    Bible,
    Character,
    ContinuityFlag,
    Location,
    Project,
    Prop,
    RenderPlan,
    Scene,
    Shot,
    ShotIntent,
)
from .video import RenderResult, VideoBackend, segment_for_veo, veo_prompt


class PipelineError(RuntimeError):
    """The pipeline could not produce a complete project.

    Raised where the alternative would be to carry on with a film that is
    quietly missing a shot. An agent returning malformed output is a
    recoverable condition — a shot disappearing from the plan without anyone
    noticing is not.
    """


def _shots_for_scene(
    scene: Scene, raw_shots: list[dict], seen_shot_ids: set[str]
) -> list[Shot]:
    """Build one scene's shots, refusing to lose any of them silently.

    The cinematographer is a language model and its output is a proposal.
    Shots belonging to another scene are rejected rather than dropped on the
    floor, because a shot filtered out here would never appear in the plan,
    never be rendered, and never be missed. Duplicate ids are rejected for
    the same reason: the second one would overwrite or shadow the first.
    """
    shots: list[Shot] = []
    for raw in raw_shots:
        shot_id = raw.get("id")
        scene_id = raw.get("scene_id")
        if scene_id != scene.id:
            raise PipelineError(
                f"cinematographer returned shot {shot_id!r} with scene_id "
                f"{scene_id!r} while working on scene {scene.id!r}"
            )
        if shot_id in seen_shot_ids:
            raise PipelineError(f"duplicate shot id {shot_id!r}")
        seen_shot_ids.add(shot_id)
        shots.append(Shot(**raw))

    if not shots:
        raise PipelineError(f"cinematographer returned no shots for scene {scene.id!r}")
    return shots


def _prompt_for_shot(
    shot: Shot, raw_prompts: list[dict]
) -> tuple[dict, list[ContinuityFlag]]:
    """The one prompt belonging to `shot`, plus flags about what else came back.

    A prompter that answers with the wrong shot id used to produce nothing
    for this shot at all — the filter matched zero rows and the loop moved
    on, leaving a shot in the film with no intent behind it. That is now an
    error. Extra prompts for other shots are dropped with a warning rather
    than an error: the shot at hand still got what it needed.
    """
    flags: list[ContinuityFlag] = []
    mine = [p for p in raw_prompts if p.get("shot_id") == shot.id]
    others = {p.get("shot_id") for p in raw_prompts} - {shot.id}

    if others:
        flags.append(
            ContinuityFlag(
                target=shot.id,
                kind="warning",
                message=(
                    f"Prompter returned prompts for unrelated shots "
                    f"{sorted(str(o) for o in others)}; ignored."
                ),
            )
        )

    if not mine:
        raise PipelineError(
            f"prompter returned no prompt for shot {shot.id!r} "
            f"(it answered for {sorted(str(o) for o in others) or 'nothing'})"
        )

    if len(mine) > 1:
        flags.append(
            ContinuityFlag(
                target=shot.id,
                kind="warning",
                message=f"Prompter returned {len(mine)} prompts for this shot; used the first.",
            )
        )

    if "prompt" not in mine[0]:
        raise PipelineError(f"prompter output for shot {shot.id!r} has no 'prompt' field")

    return mine[0], flags


def _merge_bible(provided: Bible, designer_out: dict) -> Bible:
    """Merge assets-first mode: keep all provided assets byte-identical; append
    only genuinely new assets (unknown ids) from the designer's gap-fill output.
    """
    existing_char_ids = {c.id for c in provided.characters}
    existing_loc_ids = {l.id for l in provided.locations}
    existing_prop_ids = {p.id for p in provided.props}

    new_chars = [
        Character(**c)
        for c in designer_out.get("characters", [])
        if c["id"] not in existing_char_ids
    ]
    new_locs = [
        Location(**l)
        for l in designer_out.get("locations", [])
        if l["id"] not in existing_loc_ids
    ]
    new_props = [
        Prop(**p)
        for p in designer_out.get("props", [])
        if p["id"] not in existing_prop_ids
    ]

    return Bible(
        style=designer_out.get("style", provided.style),
        palette=designer_out.get("palette", provided.palette),
        mood=designer_out.get("mood", provided.mood),
        characters=list(provided.characters) + new_chars,
        locations=list(provided.locations) + new_locs,
        props=list(provided.props) + new_props,
    )


class MovieCrew:
    """Coordinates the seven role agents into a finished Project."""

    def __init__(
        self,
        llm: LLMClient,
        models: Optional[dict[str, str]] = None,
        *,
        reference_provider: Optional[ReferenceImageProvider] = None,
        reference_out_dir: str = "reference_stills",
        prompt_detail: str = "cinematic",
    ) -> None:
        self.llm = llm
        # Reserved for a future per-task model override (e.g. a custom
        # AnthropicLLMClient routing table); unused by the offline pipeline.
        self.models = models or {}
        self.reference_provider = reference_provider or NullReferenceImageProvider()
        self.reference_out_dir = reference_out_dir

        self.director = DirectorAgent(llm)
        self.writer = WriterAgent(llm)
        self.designer = DesignerAgent(llm)
        self.cinematographer = CinematographerAgent(llm)
        self.prompter = PrompterAgent(llm, detail=prompt_detail)
        self.continuity = ContinuityAgent(llm)
        self.editor = EditorAgent(llm)

    def make(self, concept: str, *, bible: Optional[Bible] = None) -> Project:
        """Run the full pipeline.

        With *bible* (assets-first mode): the writer is asked to write FOR the
        provided cast and world; the designer only fills gaps (new locations or
        props the story requires that aren't already in the library).  Provided
        assets are preserved byte-identical.

        Without *bible* (story-first, default): behaviour is unchanged.
        """
        director_out = self.director.run(concept=concept)
        title = director_out["title"]
        logline = director_out["logline"]
        outline = director_out["outline"]

        writer_out = self.writer.run(
            title=title, logline=logline, outline=outline, provided_bible=bible
        )
        raw_scenes = writer_out["scenes"]

        designer_out = self.designer.run(
            title=title, logline=logline, scenes=raw_scenes, provided_bible=bible
        )

        if bible is not None:
            effective_bible = _merge_bible(bible, designer_out)
        else:
            effective_bible = Bible(
                style=designer_out["style"],
                palette=designer_out["palette"],
                mood=designer_out["mood"],
                characters=[Character(**c) for c in designer_out["characters"]],
                locations=[Location(**l) for l in designer_out["locations"]],
                props=[Prop(**p) for p in designer_out.get("props", [])],
            )
        bible = effective_bible

        populate_reference_stills(
            bible, self.reference_provider, out_dir=self.reference_out_dir
        )

        scenes: list[Scene] = []
        all_shots: list[Shot] = []
        seen_shot_ids: set[str] = set()
        for raw_scene in raw_scenes:
            scene = Scene(**raw_scene)
            cine_out = self.cinematographer.run(scene=raw_scene)
            scene.shots = _shots_for_scene(scene, cine_out.get("shots", []), seen_shot_ids)
            scenes.append(scene)
            all_shots.extend(scene.shots)

        if not all_shots:
            raise PipelineError("the cinematographer produced no shots for any scene")

        editor_out = self.editor.run(shot_ids=[shot.id for shot in all_shots])
        order = normalize_order(all_shots, editor_out.get("order", []))
        chains = normalize_chains(all_shots, order, editor_out.get("chains", []))

        select_anchors(scenes, chains, bible)

        intents: list[ShotIntent] = []
        flags: list[ContinuityFlag] = []
        for shot in all_shots:
            prompter_out = self.prompter.run(shot=asdict(shot))
            raw_prompt, extra_flags = _prompt_for_shot(shot, prompter_out.get("prompts", []))
            flags.extend(extra_flags)

            description = raw_prompt["prompt"]
            intents.append(
                ShotIntent(
                    shot_id=shot.id,
                    description=description,
                    negative=raw_prompt.get("negative_prompt", ""),
                    duration_s=shot.duration_s,
                    aspect_ratio=DEFAULT_ASPECT_RATIO,
                )
            )
            # A Veo-specific lint, run here so its warnings reach the plan;
            # it reads a shot's text and never constrains it.
            flags.extend(veo_constraint_flags(description, shot))

        if len(intents) != len(all_shots):  # pragma: no cover - belt and braces
            raise PipelineError(
                f"expected one intent per shot ({len(all_shots)}), got {len(intents)}"
            )

        continuity_out = self.continuity.run(
            scenes=[asdict(scene) for scene in scenes],
            prompts=[asdict(intent) for intent in intents],
        )
        flags.extend(ContinuityFlag(**f) for f in continuity_out["flags"])

        for shot in all_shots:
            if shot.consistency_anchor and not shot.reference_image_ids:
                flags.append(
                    ContinuityFlag(
                        target=shot.id,
                        kind="warning",
                        message=(
                            f"Shot {shot.id} is a consistency anchor but has no "
                            "reference images attached."
                        ),
                    )
                )

        deduped_flags: dict[tuple[str, str, str], ContinuityFlag] = {}
        for flag in flags:
            deduped_flags.setdefault((flag.kind, flag.target, flag.message), flag)
        flags = list(deduped_flags.values())

        est_duration_s = sum(shot.duration_s for shot in all_shots)

        render_plan = RenderPlan(
            intents=intents,
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
        """Render every intent in project.render_plan through `backend`, in
        render_plan.order. Pure orchestration: makes no network calls itself.

        Each intent is adapted into a Veo request by `video.veo_prompt()`
        immediately before the backend sees it — the one place in the whole
        pipeline where Veo's limits apply.

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
            # An editorial chain stays whole in the plan; Veo can only carry
            # so many segments per extend-run, so the split happens here, at
            # execution, and each run restarts from its own base clip.
            for run in segment_for_veo(chain):
                in_run = len(run) >= 2
                for shot_id in run:
                    in_multishot_chain_by_shot_id[shot_id] = in_run
                for predecessor, shot_id in zip(run, run[1:]):
                    extend_from_by_shot_id[shot_id] = predecessor

        results: list[RenderResult] = []
        for shot_id in render_plan.order:
            try:
                state = resolve_shot(project, shot_id)
            except UnknownShot:
                continue
            results.append(
                backend.render(
                    veo_prompt(state.intent, reference_images=state.reference_images),
                    extend_from=extend_from_by_shot_id.get(shot_id),
                    in_multishot_chain=in_multishot_chain_by_shot_id.get(shot_id, False),
                )
            )
        return results
