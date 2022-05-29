
from typing import TYPE_CHECKING
from bpy.types import Panel
from .utils import draw_inbetween_settings
from ..ops.add import INBETWEEN_OT_add
from ..ops.remove import INBETWEEN_OT_remove
if TYPE_CHECKING:
    from bpy.types import Context


class INBETWEENS_PT_hero(Panel):

    bl_parent_id = "DATA_PT_shape_keys"
    bl_label = "In-Betweens"
    bl_description = "In-Between shape key settings"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        object = context.object
        if object is not None:
            shape = object.active_shape_key
            if shape is not None:
                key = shape.id_data
                return (key.is_property_set("in_betweens")
                        and shape.name in key.in_betweens
                        and len(key.in_betweens[shape.name]) > 0)
        return False

    def draw(self, context: 'Context') -> None:
        obj = context.object
        key = obj.data.shape_keys
        inbetweens = key.in_betweens[obj.active_shape_key.name]
        layout = self.layout

        row = layout.row()
        row.column().template_list("INBETWEENS_UL_inbetweens", "",
                                   inbetweens, "data",
                                   inbetweens, "active_index")

        column = row.column(align=True)
        column.operator_context = 'INVOKE_DEFAULT'
        column.operator(INBETWEEN_OT_add.bl_idname, text="", icon='ADD')
        column.operator(INBETWEEN_OT_remove.bl_idname, text="", icon='REMOVE')

        active = inbetweens.active
        if active:
            draw_inbetween_settings(layout, active)
