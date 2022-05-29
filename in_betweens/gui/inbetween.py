
from typing import TYPE_CHECKING
from bpy.types import Panel
from .utils import draw_inbetween_settings, layout_split
if TYPE_CHECKING:
    from bpy.types import Context


class INBETWEENS_PT_inbetween(Panel):

    bl_parent_id = "DATA_PT_shape_keys"
    bl_label = "In-Between Settings"
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
                if key.is_property_set("in_betweens"):
                    name = shape.name
                    for inbetweens in key.in_betweens:
                        if name in inbetweens.data:
                            return True
        return False

    def draw(self, context: 'Context') -> None:
        object = context.object
        target = object.active_shape_key
        name = target.name
        key = target.id_data
        for inbetweens in key.in_betweens:
            inbetween = inbetweens.data.get(name)
            if inbetween:
                layout = self.layout
                region = layout_split(layout, "Hero Shape Key")
                region.enabled = False
                region.alert = inbetweens.name not in key.key_blocks
                region.prop(inbetween, "name", icon='SHAPEKEY_DATA', text="")
                draw_inbetween_settings(layout, inbetween)
                return