
from typing import Set, TYPE_CHECKING
from bpy.types import Operator
from bpy.props import EnumProperty
from .base import COMPAT_ENGINES, COMPAT_OBJECTS
from ..lib.driver_utils import driver_remove
if TYPE_CHECKING:
    from bpy.types import Context, Event


class INBETWEEN_OT_remove(Operator):

    bl_idname = 'in_between.remove'
    bl_label = "Remove In-Between"
    bl_description = "Remove the selected in-between"
    bl_options = {'INTERNAL', 'UNDO'}

    action: EnumProperty(
        name="Action",
        items=[
            ('REMOVE', "Remove", "Remove the in-between but leave the shape key in the list"),
            ('DELETE', "Delete", "Remove and delete the in-between shape key"),
            ],
        default='DELETE',
        options=set()
        )

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        if context.engine in COMPAT_ENGINES:
            object = context.object
            if object is not None and object.type in COMPAT_OBJECTS:
                shape = object.active_shape_key
                if shape is not None:
                    key = shape.id_data
                    if key.use_relative and key.is_property_set("in_betweens"):
                        data = key.in_betweens.get(shape.name)
                        return data is not None and data.active is not None
        return False

    def draw(self, _: 'Context') -> None:
        layout = self.layout

        layout.operator(INBETWEEN_OT_remove.bl_idname,
                        text="Remove In-Between",
                        icon='REMOVE').action='REMOVE'

        layout.operator(INBETWEEN_OT_remove.bl_idname,
                        text="Delete In-Between Shape Key",
                        icon='X').action='DELETE'

    def invoke(self, context: 'Context', _: 'Event') -> Set[str]:
        context.window_manager.popup_menu(INBETWEEN_OT_remove.draw)
        return {'FINISHED'}

    def execute(self, context: 'Context') -> Set[str]:
        object = context.object
        hero = object.active_shape_key
        key = hero.id_data
        inbetweens = key.in_betweens[hero.name]
        data = inbetweens.data
        name = inbetweens.active.name
        driver_remove(key, f'key_blocks["{name}"].value')
        data.remove(data.find(name))

        if self.action == 'DELETE':
            kbs = object.data.shape_keys.key_blocks
            idx = kbs.find(name)
            if idx >= 0:
                object.shape_key_remove(kbs[idx])

        return {'FINISHED'}
