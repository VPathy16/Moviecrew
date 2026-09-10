"""The floating bar and its sidebar twin.

Two surfaces onto the same properties: a compact popover hung off the 3D
viewport header — always visible, one click from anywhere — and a full
N-panel tab for the settings behind it. Both draw `draw_body`, so they
cannot drift apart.

The split is not cosmetic. A Blender popover does not scroll: it sizes to
its content and clips whatever overflows, with no way for the user to reach
what's been cut off. So the bar carries only the per-take actions, and
anything you set once — project path, takes folder, fps — lives in the
sidebar, which scrolls.
"""

import bpy

from . import bridge

# Icon names are an RNA enum, and a wrong one raises TypeError *inside*
# draw() — which aborts the entire panel, so every control after the bad row
# silently disappears with no visible cause. Resolving through _icon() turns
# that failure into a missing icon instead of a missing UI.
_VALID_ICONS = frozenset(
    bpy.types.UILayout.bl_rna.functions["label"]
    .parameters["icon"]
    .enum_items.keys()
)


def _icon(name: str) -> str:
    return name if name in _VALID_ICONS else "NONE"


def _draw_shot_summary(layout, props) -> None:
    """What the pipeline wrote for the selected shot, before any blocking."""
    shot = bridge.find_shot(props.scene_id, props.shot_id)
    if shot is None:
        return

    box = layout.box()
    box.label(text=shot.get("description", "")[:64], icon=_icon("SEQUENCE"))
    row = box.row(align=True)
    row.label(text=shot.get("camera_move", "—"), icon=_icon("CON_CAMERASOLVER"))
    row.label(text=shot.get("lens", "—"))
    row = box.row(align=True)
    row.label(text=shot.get("framing", "—"), icon=_icon("IMAGE_PLANE"))
    row.label(text=f"{shot.get('duration_s', 0)}s")


def draw_body(layout, context, *, compact: bool = False) -> None:
    """Draw the controls.

    `compact` trims to what the floating bar can hold. A Blender popover does
    not scroll — it sizes to its content and clips the overflow — so the bar
    carries the per-take actions only, and the settings behind them live in
    the sidebar, which does scroll.
    """
    props = context.scene.moviecrew

    if not bridge.PROJECT:
        column = layout.column()
        column.label(text="No project loaded", icon=_icon("ERROR"))
        column.operator("moviecrew.load_project", icon=_icon("FILE_FOLDER"))
        return

    layout.label(text=bridge.PROJECT.get("title", "Untitled"), icon=_icon("CAMERA_DATA"))

    column = layout.column(align=True)
    column.prop(props, "scene_id", text="Scene")
    column.prop(props, "shot_id", text="Shot")

    if not compact:
        _draw_shot_summary(layout, props)

    column = layout.column(align=True)
    column.prop(props, "blocked_by", text="")
    if props.blocked_by == "AUTO":
        column.operator("moviecrew.block_shot", icon=_icon("AUTO"))
    elif not compact:
        column.label(text="Block the camera by hand", icon=_icon("INFO"))

    if not compact:
        layout.separator()
        column = layout.column(align=True)
        column.prop(props, "project_path", text="Project")
        column.prop(props, "takes_root", text="Takes")
        column.prop(props, "fps", text="FPS")

    row = layout.row()
    row.scale_y = 1.4
    row.operator("moviecrew.render_take", icon=_icon("RENDER_ANIMATION"))

    if props.shot_id and props.takes_root:
        layout.label(text=f"Next: take {props.next_take_number:03d}", icon=_icon("DOT"))
    elif not props.takes_root:
        # The bar cannot set this, so say where it lives rather than silently
        # leaving Render Take greyed out.
        layout.label(
            text="Set Takes in the sidebar" if compact else "Set a takes folder",
            icon=_icon("ERROR"),
        )


class MOVIECREW_PT_bar(bpy.types.Panel):
    """The floating bar: a popover off the viewport header."""

    bl_idname = "MOVIECREW_PT_bar"
    bl_label = "MovieCrew"
    bl_space_type = "VIEW_3D"
    bl_region_type = "HEADER"
    bl_ui_units_x = 14

    def draw(self, context):
        draw_body(self.layout, context, compact=True)


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
    self.layout.popover(panel="MOVIECREW_PT_bar", text="", icon=_icon("CAMERA_DATA"))


CLASSES = (MOVIECREW_PT_bar, MOVIECREW_PT_sidebar)


def register_header() -> None:
    bpy.types.VIEW3D_HT_header.append(_draw_header_button)


def unregister_header() -> None:
    bpy.types.VIEW3D_HT_header.remove(_draw_header_button)
