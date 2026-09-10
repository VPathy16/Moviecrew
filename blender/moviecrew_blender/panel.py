"""The floating bar and its sidebar twin.

Two surfaces onto the same properties: a compact popover hung off the 3D
viewport header — always visible, one click from anywhere — and a full
N-panel tab for when there's more to read. Both draw `draw_body`, so they
cannot drift apart.
"""

import bpy

from . import bridge


def _draw_shot_summary(layout, props) -> None:
    """What the pipeline wrote for the selected shot, before any blocking."""
    shot = bridge.find_shot(props.scene_id, props.shot_id)
    if shot is None:
        return

    box = layout.box()
    box.label(text=shot.get("description", "")[:64], icon="SEQUENCE")
    row = box.row(align=True)
    row.label(text=shot.get("camera_move", "—"), icon="CON_CAMERASOLVE")
    row.label(text=shot.get("lens", "—"))
    row = box.row(align=True)
    row.label(text=shot.get("framing", "—"), icon="IMAGE_PLANE")
    row.label(text=f"{shot.get('duration_s', 0)}s")


def draw_body(layout, context) -> None:
    props = context.scene.moviecrew

    if not bridge.PROJECT:
        column = layout.column()
        column.label(text="No project loaded", icon="ERROR")
        column.operator("moviecrew.load_project", icon="FILE_FOLDER")
        return

    layout.label(text=bridge.PROJECT.get("title", "Untitled"), icon="CAMERA_DATA")

    column = layout.column(align=True)
    column.prop(props, "scene_id", text="Scene")
    column.prop(props, "shot_id", text="Shot")

    _draw_shot_summary(layout, props)

    column = layout.column(align=True)
    column.prop(props, "blocked_by", text="Blocking")
    if props.blocked_by == "AUTO":
        column.operator("moviecrew.block_shot", icon="AUTO")
    else:
        column.label(text="Block the camera by hand", icon="INFO")

    layout.separator()

    column = layout.column(align=True)
    column.prop(props, "takes_root", text="Takes")
    column.prop(props, "fps", text="FPS")

    row = layout.row()
    row.scale_y = 1.4
    row.operator("moviecrew.render_take", icon="RENDER_ANIMATION")

    if props.shot_id and props.takes_root:
        layout.label(text=f"Next: take {props.next_take_number:03d}", icon="DOT")


class MOVIECREW_PT_bar(bpy.types.Panel):
    """The floating bar: a popover off the viewport header."""

    bl_idname = "MOVIECREW_PT_bar"
    bl_label = "MovieCrew"
    bl_space_type = "VIEW_3D"
    bl_region_type = "HEADER"
    bl_ui_units_x = 15

    def draw(self, context):
        draw_body(self.layout, context)


class MOVIECREW_PT_sidebar(bpy.types.Panel):
    """The same controls, docked in the N-panel."""

    bl_idname = "MOVIECREW_PT_sidebar"
    bl_label = "MovieCrew"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MovieCrew"

    def draw(self, context):
        draw_body(self.layout, context)


def _draw_header_button(self, context) -> None:
    self.layout.popover(panel="MOVIECREW_PT_bar", text="", icon="CAMERA_DATA")


CLASSES = (MOVIECREW_PT_bar, MOVIECREW_PT_sidebar)


def register_header() -> None:
    bpy.types.VIEW3D_HT_header.append(_draw_header_button)


def unregister_header() -> None:
    bpy.types.VIEW3D_HT_header.remove(_draw_header_button)
