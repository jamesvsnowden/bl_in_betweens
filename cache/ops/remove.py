
from typing import Set, TYPE_CHECKING
from bpy.types import Operator
from bpy.props import EnumProperty, StringProperty
from .base import COMPAT_ENGINES, COMPAT_OBJECTS
from ..lib.driver_utils import driver_remove
if TYPE_CHECKING:
    from bpy.types import Context, Event


class INBETWEEN_OT_remove(Operator):

    bl_idname = 'in_betweens.inbetween_remove'
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

    identifier: StringProperty(
        name="Identifier",
        description="Identifier of the in-between to remove (optional)",
        default="",
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
                    return key.is_property_set("in_betweens") and (shape in key.in_betweens or
                                                                   shape in key.in_betweens.heros)
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
        shape = object.active_shape_key
        key = shape.id_data
        inbetweens = key.in_betweens

        if shape in inbetweens:
            inbetween = inbetweens[shape]
        else:
            inbetween = inbetweens.search(self.identifier)
            if inbetween is None:
                self.report({'ERROR'}, (f'Search for in-between with '
                                        f'identifier {self.identifier} failed.'))
                return {'CANCELLED'}

        inbetweens.remove(inbetween, self.action == 'DELETE')
        return {'FINISHED'}
