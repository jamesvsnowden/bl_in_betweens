
from typing import Set, TYPE_CHECKING
from bpy.types import Operator
from bpy.props import StringProperty
from ..lib.asks import COMPAT_ENGINES, COMPAT_OBJECTS
if TYPE_CHECKING:
    from bpy.types import Context


class INBETWEEN_OT_activate(Operator):

    bl_idname = 'in_betweens.activate'
    bl_label = "Activate In-Between"
    bl_description = "Set the hero shape key value to the activation center of the in-between"
    bl_options = {'INTERNAL', 'UNDO'}

    identifier: StringProperty(
        name="Identifier",
        description="The identifier of the in-between",
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
                    return key.is_property_set("in_betweens") and shape in key.in_betweens
        return False

    def execute(self, context: 'Context') -> None:
        shape = context.object.active_shape_key
        inbetween = shape.id_data.in_betweens[shape]
        shape.value = inbetween.activation.center
        return {'FINISHED'}


class INBETWEEN_OT_activation_value_update(Operator):

    bl_idname = 'in_betweens.activation_value_update'
    bl_label = "Update Activation Value"
    bl_description = "Set the in-between activation center to the hero shape key value"
    bl_options = {'INTERNAL', 'UNDO'}

    identifier: StringProperty(
        name="Identifier",
        description="The identifier of the in-between",
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
                    return key.is_property_set("in_betweens") and shape in key.in_betweens
        return False

    def execute(self, context: 'Context') -> None:
        shape = context.object.active_shape_key
        inbetween = shape.id_data.in_betweens[shape]
        inbetween.activation.center = shape.value
        return {'FINISHED'}


class INBETWEEN_OT_activation_value_actions(Operator):

    bl_idname = "in_betweens.activation_value_menu"
    bl_label = "Activation Value Actions"
    bl_description = "Activation value actions menu"
    bl_options = {'INTERNAL'}

    identifier: StringProperty(
        name="Identifier",
        description="The identifier of the in-between",
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
                    return key.is_property_set("in_betweens") and shape in key.in_betweens
        return False

    def execute(self, context: 'Context') -> Set[str]:

        identifier = self.identifier

        def draw(self, _: 'Context') -> None:
            layout = self.layout

            layout.operator(INBETWEEN_OT_activate.bl_idname,
                            text="Set Hero Value To Center",
                            icon='EXPORT').identifier = identifier

            layout.operator(INBETWEEN_OT_activation_value_update.bl_idname,
                            text="Update Center From Hero Value",
                            icon='IMPORT').identifier = identifier

        context.window_manager.popup_menu(draw)
        return {'FINISHED'}
