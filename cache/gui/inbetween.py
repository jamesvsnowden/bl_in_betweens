
from typing import TYPE_CHECKING, Any, Dict
from bpy.types import Panel
from in_betweens.gui.utils import layout_split
from in_betweens.lib.curve_mapping import draw_curve_manager_ui
from ..lib.asks import split_layout
from ..ops.activation_value import INBETWEEN_OT_activation_value_actions
if TYPE_CHECKING:
    from bpy.types import Context, UILayout
    from ..api.in_between import InBetween


def draw_inbetween_settings(layout: 'UILayout',
                            inbetween: 'InBetween',
                            split_options: Dict[str, Any]) -> None:

    act = inbetween.activation
    col = split_layout(layout, "Activation", **split_options)
    row = col.row(align=True)
    row.prop(act, "center", text="Center")
    row.operator(INBETWEEN_OT_activation_value_actions.bl_idname,
                 text="",
                 icon='DOWNARROW_HLT').identifier = inbetween.identifier

    col = layout_split(layout, "Range", **dict(split_options, align=True))
    col.prop(act, "range_min", text="Min")
    col.prop(act, "range_max", text="Max")

    col = layout_split(layout, **split_options)
    draw_curve_manager_ui(col, act)
    col.prop(act, "target", text="Target")


class INBETWEENS_PT_inbetween(Panel):

    bl_parent_id = "DATA_PT_shape_keys"
    bl_label = "In-Between Settings"
    bl_description = "In-Between shape key settings"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        object = context.object
        if object is not None:
            shape = object.active_shape_key
            if shape is not None:
                key = shape.id_data
                return key.is_property_set("in_betweens") and shape in key.in_betweens
        return False

    def draw(self, context: 'Context') -> None:
        shape = context.object.active_shape_key
        draw_inbetween_settings(self.layout, shape.id_data.in_betweens[shape])
