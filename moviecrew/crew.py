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

from dataclasses import MISSING, asdict, fields
from pathlib import Path
from typing import Callable, Optional

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
from .backend import ExecutionRun, RenderResult, VideoBackend
from .rules import (
    generative_video_flags,
    normalize_chains,
    normalize_order,
    select_anchors,
)
from .cinematography import cinematic_spec_flags, compile_cinematic_spec_summary
from .schema import (
    DEFAULT_ASPECT_RATIO,
    Beat,
    Bible,
    Character,
    CinematicSpec,
    ContinuityFlag,
    Location,
    Project,
    Prop,
    RenderPlan,
    Scene,
    Shot,
    ShotIntent,
)


class PipelineError(RuntimeError):
    """The pipeline could not produce a complete project.

    Raised where the alternative would be to carry on with a film that is
    quietly missing a shot. An agent returning malformed output is a
    recoverable condition — a shot disappearing from the plan without anyone
    noticing is not.
    """


def write_checkpoint(project: Project, path: str) -> None:
    """Persist *project* to *path* as JSON, tolerating a write failure.

    Reuses exactly the serialization `Project.to_json()` and the CLI's
    `--out` already do — no new format, no database. Failure to write is
    swallowed rather than raised: a checkpoint exists to prevent data loss,
    so a checkpoint that itself crashed plan generation would be worse than
    no checkpoint at all.

    Public (not `_write_checkpoint`) because two callers need it: `make()`
    writes the pre-continuity checkpoint below, and the portal's on-demand
    continuity endpoint calls it again afterward to persist the updated
    result — same file, same format, no second mechanism.
    """
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(project.to_json(), encoding="utf-8")
    except OSError:
        pass


def run_continuity_check(
    continuity: ContinuityAgent, scenes: list[Scene], intents: list[ShotIntent]
) -> tuple[list[ContinuityFlag], bool]:
    """Run one continuity check, never letting its failure propagate.

    Returns `(flags, failed)`. On success, `flags` is exactly what
    continuity reported and `failed` is False. On any failure — an
    exception, a truncated response, JSON that parsed into the wrong shape
    — `flags` is a single project-level warning flag naming what went
    wrong and `failed` is True. This is the one place in the pipeline where
    a broad `except Exception` is deliberate: whatever continuity does
    wrong, the plan it is checking about must survive it.

    Used two ways: inline by `MovieCrew.make()` when `run_continuity=True`
    (the CLI's path — one call does everything), and separately by the
    portal, which runs plan generation and the continuity check as two
    independent requests so the second can never block the first. Same
    function either way, so the failure handling cannot drift between the
    two callers.
    """
    try:
        continuity_out = continuity.run(
            scenes=[asdict(scene) for scene in scenes],
            prompts=[asdict(intent) for intent in intents],
        )
        return [ContinuityFlag(**f) for f in continuity_out["flags"]], False
    except Exception as exc:
        # Deliberately broad: a truncated response, malformed JSON, a
        # missing "flags" key, an API failure, a raised LLMError — every one
        # of them means the same thing here, that continuity did not
        # complete, and every one of them must produce a usable result
        # rather than propagate.
        return [
            ContinuityFlag(
                target="project",
                kind="warning",
                message=(
                    "Continuity check did not complete "
                    f"({type(exc).__name__}: {exc}); this plan has not "
                    "been checked for cross-scene consistency."
                ),
            )
        ], True


# How far a scene's total shot duration may exceed its target before one
# bounded replan attempt is triggered (see Crew.make). 1.5x, not 1.0x: shot
# durations are creative judgment, not a hard cap, and re-planning on any
# overage at all would fight the cinematographer over ordinary rounding.
_DURATION_BUDGET_TOLERANCE = 1.5

# Product policy, not a renderer quirk: a shot under 5s barely registers as
# its own cut, and most video providers reject or misrender clips that
# short; a shot over 15s drags pacing even inside a long scene. Enforced
# here (not in Shot.__post_init__ — a shot in isolation cannot know it's
# violating policy any more than it can know its own cut_reason) with the
# same bounded-retry-then-clamp handling as the budget check above, so one
# model's overshoot warns and self-corrects instead of crashing the run.
MIN_SHOT_DURATION_S = 5.0
MAX_SHOT_DURATION_S = 15.0

# The LLM -> Shot boundary. Computed from Shot's own dataclass fields, never
# duplicated as a hardcoded list, so it can never drift out of sync with the
# schema: _SHOT_FIELD_NAMES is every field Shot(**...) will accept,
# _SHOT_REQUIRED_FIELD_NAMES is the subset with no default that must be
# present or the call raises a bare TypeError.
_SHOT_FIELD_NAMES = {f.name for f in fields(Shot)}
_SHOT_REQUIRED_FIELD_NAMES = {
    f.name for f in fields(Shot) if f.default is MISSING and f.default_factory is MISSING
}


def _shot_from_raw(raw: dict) -> Shot:
    """Build a Shot from the cinematographer's raw dict for it, keeping only
    the fields Shot actually declares.

    The agent is a language model, and its output routinely carries harmless
    metadata no schema asked for — "note", "rationale", and "transition"
    have all shown up in practice. `Shot(**raw)` made the whole pipeline
    brittle to any such field: a shot otherwise perfectly valid would crash
    the run with `Shot.__init__() got an unexpected keyword argument`.
    Filtering to Shot's own declared fields here means new metadata is
    silently ignored rather than either crashing or being added to the
    schema on one model's say-so. Caller (_shots_for_scene) is expected to
    have already checked every field in _SHOT_REQUIRED_FIELD_NAMES is
    present, so construction here should never itself raise.
    """
    fields_ = {k: v for k, v in raw.items() if k in _SHOT_FIELD_NAMES}
    if isinstance(fields_.get("cinematic_spec"), dict):
        fields_["cinematic_spec"] = CinematicSpec.from_dict(fields_["cinematic_spec"])
    if isinstance(fields_.get("beats"), list):
        fields_["beats"] = [Beat(**b) for b in fields_["beats"]]
    return Shot(**fields_)


def _shots_for_scene(
    scene: Scene, raw_shots: list[dict], seen_shot_ids: set[str]
) -> list[Shot]:
    """Build one scene's shots, refusing to lose any of them silently.

    The cinematographer is a language model and its output is a proposal.
    Shots belonging to another scene are rejected rather than dropped on the
    floor, because a shot filtered out here would never appear in the plan,
    never be rendered, and never be missed. Duplicate ids are rejected for
    the same reason: the second one would overwrite or shadow the first. A
    shot missing a required field is rejected the same way — with the
    shot/scene context a bare TypeError from Shot(**shot_data) would not
    have carried — rather than let one collapse the whole run confusingly.
    """
    shots: list[Shot] = []
    for raw in raw_shots:
        shot_id = raw.get("id")
        scene_id = raw.get("scene_id")

        missing = sorted(_SHOT_REQUIRED_FIELD_NAMES - raw.keys())
        if missing:
            raise PipelineError(
                f"cinematographer shot {shot_id!r} for scene {scene.id!r} is "
                f"missing required field(s) {missing}: {raw!r}"
            )
        if scene_id != scene.id:
            raise PipelineError(
                f"cinematographer returned shot {shot_id!r} with scene_id "
                f"{scene_id!r} while working on scene {scene.id!r}"
            )
        if shot_id in seen_shot_ids:
            raise PipelineError(f"duplicate shot id {shot_id!r}")
        seen_shot_ids.add(shot_id)
        shots.append(_shot_from_raw(raw))

    if not shots:
        raise PipelineError(f"cinematographer returned no shots for scene {scene.id!r}")
    # A shot in isolation cannot know its own position within its scene, so
    # this is checked here rather than in Shot.__post_init__: every shot
    # after a scene's first must say why the cut happens, or it should not
    # have been a new shot at all.
    for shot in shots[1:]:
        if shot.story_contract_version == 1 and not shot.cut_reason.strip():
            raise PipelineError(
                f"cinematographer shot {shot.id!r} in scene {scene.id!r} is missing "
                "cut_reason (every shot after a scene's first must say why the cut happens)"
            )
    return shots


def _out_of_range_shots(shots: list[Shot]) -> list[Shot]:
    """Shots whose duration_s falls outside the [MIN, MAX] pacing policy."""
    return [s for s in shots if not (MIN_SHOT_DURATION_S <= s.duration_s <= MAX_SHOT_DURATION_S)]


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

    def make(
        self,
        concept: str,
        *,
        bible: Optional[Bible] = None,
        stop_after_design: bool = False,
        approved_direction: Optional[dict] = None,
        approved_project: Optional[Project] = None,
        completed_scenes: Optional[dict[str, dict]] = None,
        strict_sequence: bool = True,
        checkpoint_path: Optional[str] = None,
        run_continuity: bool = True,
        on_progress: Optional[Callable[..., None]] = None,
        target_duration_s: Optional[float] = None,
    ) -> Project:
        """Run the pipeline: Director through Prompter, then, by default,
        the continuity check.

        *target_duration_s*, if given, is the whole film's requested
        runtime. It is divided evenly across scenes (a scene's own
        `target_duration_s`, once a smarter split is worth building, can
        override this — this call only ever fills in what a scene doesn't
        already have) and handed to the Cinematographer as a budget, not a
        suggestion: a scene that comes back badly over budget is replanned
        once with that overage named explicitly. This exists because
        nothing previously compared a shot's requested duration to what the
        narrative moment actually needed, so a plan-once fully-free
        Cinematographer would routinely turn a 10-second beat into eight
        5-second shots. None (the default) keeps every prior behavior
        exactly as it was — no budget is enforced anywhere.

        With *bible* (assets-first mode): the writer is asked to write FOR the
        provided cast and world; the designer only fills gaps (new locations or
        props the story requires that aren't already in the library).  Provided
        assets are preserved byte-identical.

        Without *bible* (story-first, default): behaviour is unchanged.

        *checkpoint_path*, if given, is written with the generated Project as
        JSON immediately before the continuity check runs (or, if
        *run_continuity* is False, is simply the last thing written — see
        below). A best-effort write: a checkpoint that cannot be written (a
        bad path, a full disk) must not itself fail plan generation, which
        is exactly the failure this exists to prevent.

        *run_continuity* (default True) is the CLI's path — one call does
        everything, continuity included, non-fatally
        (`run_continuity_check` never lets it raise). Set False to stop
        `make()` at the checkpoint and skip continuity entirely: this is
        the portal's path, so that generation — real, spent work across up
        to six agents per scene/shot — is never held up by, or lost to, the
        one call that is analysis of that work rather than part of
        producing it. A caller doing this is expected to run continuity
        itself afterward, separately, with `run_continuity_check` against
        the returned Project's own `scenes` and `render_plan.intents` —
        exactly what the portal's continuity endpoint does.

        *on_progress*, if given, is called `on_progress(event, **data)` after
        each durable pipeline milestone — never before an agent call's
        result has actually landed, so a caller reporting progress from it
        (the portal's background plan job does exactly this) is always
        reporting real, retained work, not a guess at where the pipeline is
        about to be. Events, in the order they can fire: `director_complete`,
        `writer_complete` (data: `scene_count`), `designer_complete`,
        `scene_complete` (data: `scene`, a fully-built Scene with its shots)
        — once per scene, `editor_complete` (data: `order`, `chains`,
        `shot_count`), `prompt_complete` (data: `shot_id`, `intent`) — once
        per shot, and finally `plan_complete` (data: `project`, the finished
        Project, before continuity). Omitted (the default), this is the
        plain CLI path and nothing about it changes.
        """
        sheet_notes = {}
        if approved_project is not None:
            sheet_notes = approved_project.sheet_notes
            title, logline, outline = approved_project.title, approved_project.logline, approved_project.outline
            bible = approved_project.bible
            raw_scenes = [{**asdict(scene), 'shots': []} for scene in approved_project.scenes]
        else:
            director_out = approved_direction if approved_direction is not None else self.director.run(concept=concept)
            title = director_out["title"]
            logline = director_out["logline"]
            outline = director_out["outline"]
            if on_progress:
                on_progress("director_complete")

            writer_out = self.writer.run(
                title=title, logline=logline, outline=outline, provided_bible=bible
            )
            raw_scenes = writer_out["scenes"]
            if on_progress:
                on_progress("writer_complete", scene_count=len(raw_scenes))

            designer_out = self.designer.run(
                title=title, logline=logline, scenes=raw_scenes, provided_bible=bible
            )
            if on_progress:
                on_progress("designer_complete")

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
            sheet_notes = designer_out.get("sheet_notes", {})

        # A deterministic guardrail, not a creative decision: split evenly
        # rather than asking any agent to divide it, since dividing a number
        # by a count needs no judgment. setdefault so a scene that already
        # carries its own target_duration_s (a prior make() call's split,
        # preserved through stop_after_design -> approved_project) is never
        # overwritten with a fresh, differently-rounded split.
        if target_duration_s is not None and raw_scenes:
            per_scene_default = target_duration_s / len(raw_scenes)
            for raw_scene in raw_scenes:
                raw_scene.setdefault('target_duration_s', per_scene_default)

        if stop_after_design:
            draft = Project(title=title, logline=logline, outline=outline, bible=bible, sheet_notes=sheet_notes,
                            scenes=[Scene(**{**scene, 'shots': []}) for scene in raw_scenes],
                            target_duration_s=target_duration_s)
            if checkpoint_path:
                write_checkpoint(draft, checkpoint_path)
            return draft

        populate_reference_stills(
            bible, self.reference_provider, out_dir=self.reference_out_dir
        )

        scenes: list[Scene] = []
        all_shots: list[Shot] = []
        seen_shot_ids: set[str] = set()
        duration_flags: list[ContinuityFlag] = []
        for raw_scene in raw_scenes:
            scene = Scene(**raw_scene)
            cached_scene = (completed_scenes or {}).get(scene.id)
            cine_out = cached_scene if cached_scene is not None else self.cinematographer.run(scene=raw_scene)
            scene.shots = _shots_for_scene(scene, cine_out.get("shots", []), seen_shot_ids)

            # A cached scene was already accepted in an earlier run; only a
            # freshly-planned scene gets budget/pacing-checked and, if
            # needed, one bounded replan attempt — never an unbounded retry
            # loop. Budget (aggregate, target-driven) and pacing (per-shot,
            # always-on [MIN,MAX] policy) are independent problems, but a
            # single scene can have both at once, so they share one retry.
            if cached_scene is None:
                total = sum(shot.duration_s for shot in scene.shots)
                over_budget = bool(scene.target_duration_s) and total > scene.target_duration_s * _DURATION_BUDGET_TOLERANCE
                out_of_range = _out_of_range_shots(scene.shots)
                if over_budget or out_of_range:
                    seen_shot_ids.difference_update(shot.id for shot in scene.shots)
                    notice_parts = []
                    if over_budget:
                        notice_parts.append(
                            f"Your previous attempt planned {len(scene.shots)} shots totalling "
                            f"{total:.1f}s against a {scene.target_duration_s:.0f}s target for "
                            "this scene - well over budget. Combine micro-actions (expression "
                            "changes, eyeline shifts, small movements) into beats within fewer, "
                            "longer shots instead of cutting for each one. Only create a new "
                            "shot when cut_reason names a real editorial reason. Keep total "
                            "shot duration close to the target."
                        )
                    if out_of_range:
                        detail = ", ".join(f"{shot.id} at {shot.duration_s:.1f}s" for shot in out_of_range)
                        notice_parts.append(
                            f"Every shot's duration_s must be between {MIN_SHOT_DURATION_S:.0f} and "
                            f"{MAX_SHOT_DURATION_S:.0f} seconds - a hard production limit, not a "
                            f"suggestion. Out of range last attempt: {detail}. Vary durations across "
                            "shots to match what each beat actually needs within that range; giving "
                            "every shot the same duration reads as monotonous, mechanical cutting."
                        )
                    overage_scene = {**raw_scene, "over_budget_notice": " ".join(notice_parts)}
                    cine_out = self.cinematographer.run(scene=overage_scene)
                    scene.shots = _shots_for_scene(scene, cine_out.get("shots", []), seen_shot_ids)
                    retotal = sum(shot.duration_s for shot in scene.shots)
                    if over_budget and retotal > scene.target_duration_s * _DURATION_BUDGET_TOLERANCE:
                        duration_flags.append(ContinuityFlag(
                            target=scene.id, kind="warning",
                            message=(
                                f"Scene {scene.id} used {retotal:.1f}s of shots against a "
                                f"{scene.target_duration_s:.0f}s target even after one replan "
                                "attempt."
                            ),
                        ))
                    still_out_of_range = _out_of_range_shots(scene.shots)
                    if still_out_of_range:
                        detail = ", ".join(f"{shot.id} ({shot.duration_s:.1f}s)" for shot in still_out_of_range)
                        for shot in still_out_of_range:
                            shot.duration_s = min(MAX_SHOT_DURATION_S, max(MIN_SHOT_DURATION_S, shot.duration_s))
                        duration_flags.append(ContinuityFlag(
                            target=scene.id, kind="warning",
                            message=(
                                f"Scene {scene.id} still had shot(s) outside the "
                                f"{MIN_SHOT_DURATION_S:.0f}-{MAX_SHOT_DURATION_S:.0f}s pacing policy "
                                f"after one replan attempt and was clamped to fit: {detail}."
                            ),
                        ))

            scenes.append(scene)
            all_shots.extend(scene.shots)
            if on_progress:
                on_progress("scene_complete", scene=scene)

        if not all_shots:
            raise PipelineError("the cinematographer produced no shots for any scene")

        from .story_direction import COMPILER_VERSION, check_sequence, prompt_context
        editor_out = self.editor.run(shot_ids=[shot.id for shot in all_shots], context={
            'title':title, 'logline':logline, 'outline':outline,
            'scenes':[asdict(scene) for scene in scenes]})
        order = normalize_order(all_shots, editor_out.get("order", []))
        chains = normalize_chains(all_shots, order, editor_out.get("chains", []))

        notes = editor_out.get('editorial_notes', {})
        if not isinstance(notes, dict):
            raise PipelineError('Editor notes must map shot IDs to reasons')
        notes = {k:v for k,v in notes.items() if k in order and isinstance(v,str)}
        try:
            direction_flags = check_sequence(all_shots, order, strict=strict_sequence)
        except ValueError as exc:
            raise PipelineError(str(exc)) from exc
        select_anchors(scenes, chains, bible)
        if on_progress:
            on_progress("editor_complete", order=order, chains=chains, shot_count=len(all_shots))

        intents: list[ShotIntent] = []
        flags: list[ContinuityFlag] = list(direction_flags) + duration_flags
        for shot in all_shots:
            context = prompt_context(shot, scenes, order, bible, title, logline, outline, notes,
                                     world_approved=approved_project is not None)
            if shot.cinematic_spec is not None:
                # The compiled, resolved phrase — not the raw spec (already
                # present via context['current_shot']) and not its
                # rationale: only what's actually render-relevant reaches
                # the prompt-writing step from here.
                context['cinematic_direction'] = compile_cinematic_spec_summary(shot.cinematic_spec)
            prompter_out = self.prompter.run(shot=asdict(shot), context=context)
            raw_prompt, extra_flags = _prompt_for_shot(shot, prompter_out.get("prompts", []))
            flags.extend(extra_flags)

            description = raw_prompt["prompt"]
            intent = ShotIntent(
                shot_id=shot.id,
                description=description,
                negative=raw_prompt.get("negative_prompt", ""),
                duration_s=shot.duration_s,
                aspect_ratio=DEFAULT_ASPECT_RATIO,
                compiler_version=COMPILER_VERSION,
                direction_context=context,
            )
            intents.append(intent)
            # Lints, run here so their warnings reach the plan; they read a
            # shot's text/spec and warn, and never constrain it.
            flags.extend(generative_video_flags(description, shot))
            flags.extend(cinematic_spec_flags(shot))
            if on_progress:
                on_progress("prompt_complete", shot_id=shot.id, intent=intent)

        if len(intents) != len(all_shots):  # pragma: no cover - belt and braces
            raise PipelineError(
                f"expected one intent per shot ({len(all_shots)}), got {len(intents)}"
            )

        # Independent of continuity's own output, so computed and folded in
        # before continuity runs: a warning here must not be lost just
        # because the call after it fails.
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

        est_duration_s = sum(shot.duration_s for shot in all_shots)
        if target_duration_s and est_duration_s > target_duration_s * _DURATION_BUDGET_TOLERANCE:
            flags.append(ContinuityFlag(
                target="project", kind="warning",
                message=(
                    f"Planned runtime is {est_duration_s:.1f}s against a "
                    f"{target_duration_s:.0f}s target, even after per-scene budgeting."
                ),
            ))

        # Everything above this line is real, spent generation — up to six
        # agent calls per scene/shot. The Project built here is already
        # complete and usable; continuity below is a check *on* it, not a
        # precondition *of* it, so its failure must never cost what already
        # exists. `flags` is the same list `render_plan` holds, so appending
        # to it after this point (on success or on failure) still reaches
        # the Project already returned to a caller that read render_plan
        # directly — but the final dedup pass below reassigns the list, so
        # it is `render_plan.flags` (not `flags`) that gets that update.
        render_plan = RenderPlan(
            intents=intents,
            flags=flags,
            order=order,
            chains=chains,
            est_duration_s=est_duration_s,
            editorial_notes=notes,
        )
        project = Project(
            title=title,
            logline=logline,
            bible=bible,
            outline=outline,
            scenes=scenes,
            render_plan=render_plan,
            sheet_notes=sheet_notes,
            target_duration_s=target_duration_s,
        )

        if checkpoint_path:
            write_checkpoint(project, checkpoint_path)

        if on_progress:
            on_progress("plan_complete", project=project)

        if run_continuity:
            continuity_flags, _failed = run_continuity_check(self.continuity, scenes, intents)
            flags.extend(continuity_flags)

            deduped_flags: dict[tuple[str, str, str], ContinuityFlag] = {}
            for flag in flags:
                deduped_flags.setdefault((flag.kind, flag.target, flag.message), flag)
            render_plan.flags = list(deduped_flags.values())

        return project

    def plan_execution(
        self, project: Project, backend: VideoBackend
    ) -> list[ExecutionRun]:
        """How `backend` will actually execute this plan's editorial chains.

        An editorial chain stays whole in the plan; a backend that can only
        carry so much of a take in one piece splits it here, at execution,
        and each run restarts from its own base clip. The runs are returned
        rather than kept private because assembly needs them: which clips
        carry the footage depends on how the work was split and on what the
        backend's clips contain, and neither is knowable from the canonical
        chains alone.
        """
        render_plan = project.render_plan
        if render_plan is None:
            return []

        runs: list[ExecutionRun] = []
        for chain in render_plan.chains:
            for run in backend.segment(chain):
                if not run:
                    continue
                runs.append(
                    ExecutionRun(
                        chain=tuple(chain),
                        shot_ids=tuple(run),
                        output=backend.chain_output,
                    )
                )
        return runs

    def render(self, project: Project, backend: VideoBackend) -> list[RenderResult]:
        """Render every intent in project.render_plan through `backend`, in
        render_plan.order. Pure orchestration: makes no network calls itself,
        and names no vendor.

        Each intent is adapted by the backend's own `adapt()` immediately
        before it renders — the one moment in the whole pipeline where any
        backend's limits apply. This method never builds a request itself,
        which is what lets the same plan run on Veo, on a generative API, or
        on anything else that implements the interface.

        Chain-aware: an editorial chain is kept whole in the plan, and the
        backend says via `segment()` how much of it can be executed in one
        piece. Within a run, each shot after the first is rendered with
        extend_from set to its predecessor's shot id; a run's first shot (or
        a standalone shot) gets extend_from=None. Every shot in a run of 2+
        is passed in_multishot_chain=True, since some backends must render a
        continuable shot differently from a standalone one.
        """
        render_plan = project.render_plan
        if render_plan is None:
            return []

        runs = self.plan_execution(project, backend)
        extend_from_by_shot_id: dict[str, Optional[str]] = {}
        in_multishot_chain_by_shot_id: dict[str, bool] = {}
        for run in runs:
            in_run = len(run.shot_ids) >= 2
            for shot_id in run.shot_ids:
                in_multishot_chain_by_shot_id[shot_id] = in_run
            for predecessor, shot_id in zip(run.shot_ids, run.shot_ids[1:]):
                extend_from_by_shot_id[shot_id] = predecessor

        results: list[RenderResult] = []
        for shot_id in render_plan.order:
            try:
                state = resolve_shot(project, shot_id)
            except UnknownShot:
                continue
            results.append(
                backend.render(
                    backend.adapt(state.intent, reference_images=state.reference_images),
                    extend_from=extend_from_by_shot_id.get(shot_id),
                    in_multishot_chain=in_multishot_chain_by_shot_id.get(shot_id, False),
                )
            )
        return results
