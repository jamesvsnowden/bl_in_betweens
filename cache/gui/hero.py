
from typing import TYPE_CHECKING, Any, Dict, Optional
from bpy.types import Panel
from ..lib.asks import split_layout
if TYPE_CHECKING:
    from bpy.types import Context, UILayout
    from ..api.hero import InBetweenHero


def draw_hero_settings(layout: 'UILayout',
                       hero: 'InBetweenHero',
                       label: Optional[str]="In-Betweens",
                       **split_options: Dict[str, Any]) -> None:

    column = split_layout(layout, label, **split_options)
    column.operator("in_betweens.inbetween_add", text="Add", icon='ADD')

    for inbetween in hero.in_betweens:
        row = column.row()

        row.prop(inbetween.activation, "center", text="")

        row.operator("in_betweens.settings_popup",
                     text="",
                     icon='SETTINGS',
                     emboss=False).identifier = inbetween.identifier

        row.separator()

        row.operator("in_betweens.inbetween_remove",
                     text="",
                     icon='X',
                     emboss=False).identifier = inbetween.identifier
    

class INBETWEENS_PT_hero_settings(Panel):

    bl_parent_id = "DATA_PT_shape_keys"
    bl_label = "In-Betweens"
    bl_description = "In-Between shape keys"
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
                return key.is_property_set("in_betweens") and shape in key.in_betweens.heros
        return False

    def draw(self, context: 'Context') -> None:
        shape = context.object.active_shape_key
        key = shape.id_data
        draw_hero_settings(self.layout, key.in_betweens.heros[shape])
