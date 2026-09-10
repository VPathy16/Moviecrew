"""MovieCrew for Blender: block a shot from the pipeline, render it as a take.

The pipeline writes `project.json` (scenes, shots, and the cinematographer's
`camera_move` / `lens` / `framing`). This add-on picks a scene and shot out of
it, blocks the camera — either automatically from that written cinematography
or by hand — and renders the result as the next numbered take under a takes
root that the MovieCrew portal reads.

No `bl_info`: this is a Blender 4.2+ extension, described by
`blender_manifest.toml` instead.
"""

import bpy

from . import bridge, operators, panel
from .panel import _icon

# Blender's dynamic EnumProperty items must be kept alive by Python or the
# strings are garbage-collected out from under the UI — a well-known way to
# corrupt or crash the enum. Holding the tuples here is the standard fix.
_ENUM_CACHE: dict[str, list[tuple[str, str, str]]] = {"scenes": [], "shots": []}


def _scene_items(self, context):
    items = [
        (scene.get("id", ""), scene.get("title", scene.get("id", "")), scene.get("summary", "")[:80])
        for scene in bridge.scenes()
        if scene.get("id")
    ]
    _ENUM_CACHE["scenes"] = items or [("", "No scenes", "")]
    return _ENUM_CACHE["scenes"]


def _shot_items(self, context):
    items = [
        (shot.get("id", ""), shot.get("id", ""), shot.get("description", "")[:80])
        for shot in bridge.shots_in(self.scene_id)
        if shot.get("id")
    ]
    _ENUM_CACHE["shots"] = items or [("", "No shots", "")]
    return _ENUM_CACHE["shots"]


def _next_take_number(self) -> int:
    """Read-only display of the number the next render would claim."""
    if not (self.takes_root and self.scene_id and self.shot_id):
        return 1
    error = bridge.ensure_moviecrew_importable(
        bpy.context.preferences.addons[__package__].preferences.moviecrew_path
    )
    if error:
        return 1
    from moviecrew.takes import next_take_number

    return next_take_number(
        bpy.path.abspath(self.takes_root), self.scene_id, self.shot_id
    )


class MovieCrewPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    moviecrew_path: bpy.props.StringProperty(
        name="MovieCrew Repository",
        description=(
            "Folder containing the 'moviecrew' package. Leave empty if "
            "MovieCrew is already installed into Blender's Python"
        ),
        subtype="DIR_PATH",
    )

    def draw(self, context):
        column = self.layout.column()
        column.prop(self, "moviecrew_path")
        error = bridge.ensure_moviecrew_importable(self.moviecrew_path)
        if error:
            column.label(text=error, icon=_icon("ERROR"))
        else:
            column.label(text="MovieCrew package found", icon=_icon("CHECKMARK"))


class MovieCrewProperties(bpy.types.PropertyGroup):
    project_path: bpy.props.StringProperty(
        name="Project", description="The loaded project.json", subtype="FILE_PATH"
    )
    takes_root: bpy.props.StringProperty(
        name="Takes Root",
        description="Folder that takes are written under, read by the MovieCrew portal",
        subtype="DIR_PATH",
    )
    scene_id: bpy.props.EnumProperty(
        name="Scene", description="Scene from the project", items=_scene_items
    )
    shot_id: bpy.props.EnumProperty(
        name="Shot", description="Shot within the selected scene", items=_shot_items
    )
    blocked_by: bpy.props.EnumProperty(
        name="Blocking",
        description="Where this take's camera move comes from",
        items=[
            (
                "AUTO",
                "From Shot",
                "Block the camera from the cinematography the pipeline wrote",
            ),
            ("MANUAL", "By Hand", "Block the camera yourself; the take records that"),
        ],
        default="AUTO",
    )
    fps: bpy.props.IntProperty(
        name="FPS", description="Frames per second for blocking and render", default=24, min=1, max=240
    )
    next_take_number: bpy.props.IntProperty(
        name="Next Take", get=_next_take_number
    )


CLASSES = (MovieCrewPreferences, MovieCrewProperties, *operators.CLASSES, *panel.CLASSES)


def register() -> None:
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.moviecrew = bpy.props.PointerProperty(type=MovieCrewProperties)
    panel.register_header()


def unregister() -> None:
    panel.unregister_header()
    operators._unsubscribe()
    del bpy.types.Scene.moviecrew
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
