"""Operators: load a project, block a shot, render a take.

Rendering is deliberately *not* driven with a blocking `bpy.ops.render.render()`
call. Blender's UI is single-threaded, so a blocking render freezes the whole
application until it finishes. Instead the render is invoked non-modally and a
`render_complete` handler finishes the job — writing the take record only once
Blender says the file exists.
"""

from pathlib import Path
from typing import Any, Optional

import bpy
from bpy.app.handlers import persistent

from . import bridge

# Set between invoking a render and its completion handler firing.
_PENDING: dict[str, Any] = {}


def _prefs(context) -> Any:
    return context.preferences.addons[__package__].preferences


def _report_error(operator, message: str) -> set[str]:
    operator.report({"ERROR"}, message)
    return {"CANCELLED"}


def _require_moviecrew(operator, context) -> Optional[str]:
    return bridge.ensure_moviecrew_importable(_prefs(context).moviecrew_path)


class MOVIECREW_OT_load_project(bpy.types.Operator):
    """Load a project.json produced by the MovieCrew pipeline"""

    bl_idname = "moviecrew.load_project"
    bl_label = "Load MovieCrew Project"
    bl_options = {"REGISTER", "UNDO"}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.json", options={"HIDDEN"})

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        error = _require_moviecrew(self, context)
        if error:
            return _report_error(self, error)

        error = bridge.load_project(self.filepath)
        if error:
            return _report_error(self, error)

        props = context.scene.moviecrew
        props.project_path = bridge.PROJECT_PATH

        scenes = bridge.scenes()
        if scenes:
            props.scene_id = scenes[0].get("id", "")

        self.report(
            {"INFO"},
            f"Loaded {bridge.PROJECT.get('title', 'project')} — {len(scenes)} scene(s)",
        )
        return {"FINISHED"}


class MOVIECREW_OT_block_shot(bpy.types.Operator):
    """Key the active camera from the shot's written cinematography"""

    bl_idname = "moviecrew.block_shot"
    bl_label = "Auto-Block Shot"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return bool(context.scene.moviecrew.shot_id) and context.scene.camera is not None

    def execute(self, context):
        error = _require_moviecrew(self, context)
        if error:
            return _report_error(self, error)

        props = context.scene.moviecrew
        shot = bridge.find_shot(props.scene_id, props.shot_id)
        if shot is None:
            return _report_error(self, f"Shot {props.shot_id!r} is not in the project")

        camera = context.scene.camera
        if camera is None:
            return _report_error(self, "No active camera in this scene")

        blocking = bridge.block_for(shot, fps=props.fps)
        bridge.apply_blocking(camera, blocking, context.scene)

        # Notes are the honest part: they say which phrases were not
        # understood and were defaulted, so an operator knows exactly where
        # the automatic block needs a human eye.
        if blocking.notes:
            for note in blocking.notes:
                self.report({"WARNING"}, note)
        else:
            self.report({"INFO"}, f"Blocked {props.shot_id} as {blocking.move}")
        return {"FINISHED"}


@persistent
def _on_render_finished(*args) -> None:
    """Write the take record once Blender's output actually exists."""
    if not _PENDING:
        return

    pending = dict(_PENDING)
    _PENDING.clear()
    _unsubscribe()

    try:
        from moviecrew.takes import resolve_video, save_take

        take = pending["take"]
        root = pending["root"]
        destination = resolve_video(take, root)
        landed = bridge.claim_rendered_file(
            Path(pending["directory"]), pending["stem"], destination
        )
        if landed is None:
            print(f"[moviecrew] render produced no file for {take.take_id}")
            return
        save_take(take, root)
        print(f"[moviecrew] saved {take.take_id} -> {landed}")
    except Exception as exc:  # never let a handler break Blender's render
        print(f"[moviecrew] failed to record take: {exc}")


@persistent
def _on_render_cancelled(*args) -> None:
    _PENDING.clear()
    _unsubscribe()


def _subscribe() -> None:
    if _on_render_finished not in bpy.app.handlers.render_complete:
        bpy.app.handlers.render_complete.append(_on_render_finished)
    if _on_render_cancelled not in bpy.app.handlers.render_cancel:
        bpy.app.handlers.render_cancel.append(_on_render_cancelled)


def _unsubscribe() -> None:
    if _on_render_finished in bpy.app.handlers.render_complete:
        bpy.app.handlers.render_complete.remove(_on_render_finished)
    if _on_render_cancelled in bpy.app.handlers.render_cancel:
        bpy.app.handlers.render_cancel.remove(_on_render_cancelled)


class MOVIECREW_OT_render_take(bpy.types.Operator):
    """Render the current camera as the next take of the selected shot"""

    bl_idname = "moviecrew.render_take"
    bl_label = "Render Take"

    @classmethod
    def poll(cls, context):
        props = context.scene.moviecrew
        return bool(props.shot_id and props.takes_root) and context.scene.camera is not None

    def execute(self, context):
        error = _require_moviecrew(self, context)
        if error:
            return _report_error(self, error)

        props = context.scene.moviecrew
        shot = bridge.find_shot(props.scene_id, props.shot_id)
        if shot is None:
            return _report_error(self, f"Shot {props.shot_id!r} is not in the project")
        if _PENDING:
            return _report_error(self, "A take is already rendering")

        from moviecrew.takes import (
            BLOCKED_BY_AUTO,
            BLOCKED_BY_MANUAL,
            new_take_for_shot,
            resolve_video,
            take_stem,
        )

        root = Path(bpy.path.abspath(props.takes_root))
        blocking = bridge.block_for(shot, fps=props.fps)

        take = new_take_for_shot(
            bridge._ShotView(shot),
            props.scene_id,
            root,
            blocked_by=BLOCKED_BY_AUTO if props.blocked_by == "AUTO" else BLOCKED_BY_MANUAL,
            resolution=f"{context.scene.render.resolution_x}x{context.scene.render.resolution_y}",
            fps=props.fps,
        )

        destination = resolve_video(take, root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        stem = take_stem(take.take_number)

        bridge.configure_video_render(
            context.scene, str(destination.parent / stem), blocking
        )

        _PENDING.update(
            {
                "take": take,
                "root": root,
                "directory": str(destination.parent),
                "stem": stem,
            }
        )
        _subscribe()

        # INVOKE_DEFAULT opens Blender's own render window and returns
        # immediately, so the UI stays responsive while frames render.
        bpy.ops.render.render("INVOKE_DEFAULT", animation=True)
        self.report({"INFO"}, f"Rendering {take.take_id}")
        return {"FINISHED"}


CLASSES = (
    MOVIECREW_OT_load_project,
    MOVIECREW_OT_block_shot,
    MOVIECREW_OT_render_take,
)
