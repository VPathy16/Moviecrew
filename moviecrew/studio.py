"""Studio session state machine for iterative project development.

Stages:  CONCEPT → SHOT_DEFS → STORYBOARD → OUTPUT

At STORYBOARD, one still image is generated per shot (via an ImageProvider),
presented for human review, and on approval the anchored shots' board images
are promoted to their reference_image_ids so the eventual Veo render can anchor
character consistency off the approved frame.

Nothing here calls any video-render API — that is the OUTPUT / render step.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

from .image import ImageProvider, NullImageProvider
from .schema import Project


class Stage(str, Enum):
    CONCEPT = "concept"
    SHOT_DEFS = "shot_defs"
    STORYBOARD = "storyboard"
    OUTPUT = "output"


@dataclass
class StoryboardFrame:
    shot_id: str
    prompt_used: str
    status: str               # "ok" | "failed"
    image_path: Optional[str] = None
    # Stashed by approve() when promotes_references is True; restored by revise().
    prior_reference_image_ids: Optional[list[str]] = None


# Sentence-level prefixes that signal camera-motion intent in a Veo prompt.
_CAMERA_STARTS = (
    "camera ", "shot on ", "cut to ", "cut from ", "pan ", "tilt ", "dolly ",
    "zoom ", "push ", "pull ", "crane ", "fly ", "slow dolly", "fast dolly",
    "tracking ", "track ", "aerial ", "handheld ", "steadicam ",
)

# Pattern for sentences whose sole content is a sound description.
_SOUND_ONLY_RE = re.compile(
    r"^[^.!?;]*"
    r"(roars?|crashes?|creaks?|patters?|gusts?|groans?|howls?|hisses?|"
    r"rumbles?|thuds?|clanks?|echoes?|whistles?|drips?|sizzles?)"
    r"[,.\s]",
    re.IGNORECASE,
)


def _veo_to_still_prompt(veo_prompt: str) -> str:
    """Distil a motion-first Veo prompt to a composed still-frame description.

    Keeps subject, wardrobe, setting, light, and lens cues; strips camera-
    motion sentences and pure-sound sentences so the image model receives a
    static composition rather than an action sequence.
    """
    parts = re.split(r"(?<=[.!?;])\s+", veo_prompt)
    kept = []
    for part in parts:
        p = part.strip()
        if not p:
            continue
        lower = p.lower()
        if any(lower.startswith(cam) for cam in _CAMERA_STARTS):
            continue
        if _SOUND_ONLY_RE.match(p):
            continue
        kept.append(p)
    result = " ".join(kept) if kept else veo_prompt
    return f"Still frame: {result}"


@dataclass
class StudioSession:
    """Single creative session tracking stage, project, and storyboard state.

    Lifecycle::

        session = StudioSession(...)            # stage = SHOT_DEFS
        session.produce()                       # -> STORYBOARD; generates images
        session.revise(shot_id="sc1-sh1")       # re-generate one frame
        session.approve()                       # -> OUTPUT; promotes anchors
    """

    session_id: str
    stage: Stage
    project: Project
    session_dir: str
    image_provider: ImageProvider = field(repr=False, default_factory=NullImageProvider)
    board: list[StoryboardFrame] = field(default_factory=list)

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def produce(self) -> None:
        """Generate one storyboard image per shot.  Transitions to STORYBOARD.

        A provider failure records a "failed" frame and continues — the board
        is never aborted mid-generation.  Safe to call again (regenerates all).
        """
        board_dir = Path(self.session_dir) / "storyboard"
        board_dir.mkdir(parents=True, exist_ok=True)

        prompts_by_shot_id = {
            intent.shot_id: intent.description
            for intent in (
                self.project.render_plan.intents if self.project.render_plan else []
            )
        }

        self.board = []
        for scene in self.project.scenes:
            for shot in scene.shots:
                shot_text = prompts_by_shot_id.get(shot.id, shot.description)
                still_prompt = _veo_to_still_prompt(shot_text)
                frame = self._generate_frame(shot.id, still_prompt, board_dir)
                self.board.append(frame)

        self.stage = Stage.STORYBOARD

    def approve(self) -> None:
        """Promote each anchored shot's ok frame into its reference_image_ids.

        Advances stage to OUTPUT.  Promotion only happens when the image
        provider declares promotes_references=True (real generators); with
        Null/Mock providers the existing reference_image_ids are left
        untouched so hand-supplied library stills survive.  When promoting,
        the board image is PREPENDED and nothing is dropped: the approved
        frame is the most important reference, and a backend that accepts
        fewer takes the first N at its own boundary.  Truncating here would
        discard a still the production deliberately attached, to satisfy a
        limit belonging to whichever renderer happened to be configured.
        The pre-promotion list is stashed on the frame so revise() can
        restore it.
        """
        frames_by_shot_id = {f.shot_id: f for f in self.board}

        for scene in self.project.scenes:
            for shot in scene.shots:
                frame = frames_by_shot_id.get(shot.id)
                if not (shot.consistency_anchor and frame and frame.status == "ok"):
                    continue
                if not self.image_provider.promotes_references:
                    continue
                frame.prior_reference_image_ids = list(shot.reference_image_ids)
                shot.reference_image_ids = [frame.image_path] + shot.reference_image_ids

        self.stage = Stage.OUTPUT

    def revise(self, feedback: str = "", shot_id: Optional[str] = None) -> None:
        """Regenerate a single frame or the entire board.

        If *shot_id* is given, only that frame is regenerated (keeping the rest
        of self.board intact) and any reference promotion for that shot is
        cleared.  Without *shot_id*, the whole board is regenerated.
        Reverts stage to STORYBOARD (allowing a fresh approve() pass).
        """
        board_dir = Path(self.session_dir) / "storyboard"
        board_dir.mkdir(parents=True, exist_ok=True)

        prompts_by_shot_id = {
            intent.shot_id: intent.description
            for intent in (
                self.project.render_plan.intents if self.project.render_plan else []
            )
        }

        if shot_id:
            self._revise_one(shot_id, feedback, board_dir, prompts_by_shot_id)
        else:
            old_frames_by_shot_id = {f.shot_id: f for f in self.board}
            new_board = []
            for scene in self.project.scenes:
                for shot in scene.shots:
                    old_frame = old_frames_by_shot_id.get(shot.id)
                    if old_frame and old_frame.prior_reference_image_ids is not None:
                        shot.reference_image_ids = old_frame.prior_reference_image_ids
                    veo_prompt = prompts_by_shot_id.get(shot.id, shot.description)
                    still_prompt = _build_still_with_feedback(veo_prompt, feedback)
                    new_board.append(self._generate_frame(shot.id, still_prompt, board_dir))
            self.board = new_board

        self.stage = Stage.STORYBOARD

    # ------------------------------------------------------------------ #
    # Internals                                                            #
    # ------------------------------------------------------------------ #

    def _generate_frame(
        self, shot_id: str, still_prompt: str, board_dir: Path
    ) -> StoryboardFrame:
        try:
            image_bytes = self.image_provider.generate(still_prompt, shot_id)
            image_path = str(board_dir / f"{shot_id}.png")
            Path(image_path).write_bytes(image_bytes)
            return StoryboardFrame(
                shot_id=shot_id,
                prompt_used=still_prompt,
                status="ok",
                image_path=image_path,
            )
        except Exception:
            return StoryboardFrame(
                shot_id=shot_id,
                prompt_used=still_prompt,
                status="failed",
                image_path=None,
            )

    def _revise_one(
        self,
        shot_id: str,
        feedback: str,
        board_dir: Path,
        prompts_by_shot_id: dict[str, str],
    ) -> None:
        old_frame = next((f for f in self.board if f.shot_id == shot_id), None)

        for scene in self.project.scenes:
            for shot in scene.shots:
                if shot.id == shot_id:
                    if old_frame and old_frame.prior_reference_image_ids is not None:
                        # Restore the stash set by approve() rather than clearing to [].
                        shot.reference_image_ids = old_frame.prior_reference_image_ids
                    break

        veo_prompt = prompts_by_shot_id.get(shot_id, shot_id)
        still_prompt = _build_still_with_feedback(veo_prompt, feedback)
        new_frame = self._generate_frame(shot_id, still_prompt, board_dir)

        # Replace the existing frame for this shot_id, or append if missing.
        for i, frame in enumerate(self.board):
            if frame.shot_id == shot_id:
                self.board[i] = new_frame
                return
        self.board.append(new_frame)


def _build_still_with_feedback(veo_prompt: str, feedback: str) -> str:
    base = _veo_to_still_prompt(veo_prompt)
    return f"{base} Revision note: {feedback}" if feedback else base
