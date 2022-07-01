
from typing import Set, TYPE_CHECKING
from bpy.types import Operator
from bpy.props import StringProperty
from ..gui.inbetween import draw_inbetween_settings
if TYPE_CHECKING:
    from bpy.types import Context


class INBETWEENS_OT_settings_popup(Operator):

    bl_idname = 'in_betweens.settings_popup'
    bl_label = "In-Between Settings"
    bl_description = "Adjust in-between settings"
    bl_options = {'INTERNAL', 'UNDO'}

    identifier: StringProperty(
        name="In-Between",
        description="Identifier of the in-between",
        default="",
        options=set()
        )

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        object = context.object
        if object is not None:
            shape = object.active_shape_key
            return shape is not None and shape.id_data.is_property_set("in_betweens")
        return False

    def draw(self, context: 'Context') -> None:
        identifier = self.identifier
        inbetweens = context.object.active_shape_key.id_data.in_betweens
        draw_inbetween_settings(self.layout, inbetweens.search(identifier))

    def invoke(self, context: 'Context', _) -> Set[str]:
        identifier = self.identifier
        inbetweens = context.object.active_shape_key.id_data.in_betweens

        inbetween = inbetweens.search(identifier)
        if inbetween is None:
            self.report({'ERROR'}, "In-between not found")
            return {'CANCELLED'}

        return context.window_manager.invoke_popup(self)

    def execute(self, _) -> None:
        return {'FINISHED'}