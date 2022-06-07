
from typing import Set, TYPE_CHECKING
from bpy.types import Operator
from bpy.props import StringProperty
from .base import COMPAT_ENGINES, COMPAT_OBJECTS
if TYPE_CHECKING:
    from bpy.types import Context, ShapeKey
    from ..api.in_between import InBetween
    from ..api.in_betweens import InBetweens


class ActivationValue:
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
                    if key.use_relative and key.is_property_set("in_betweens"):
                        data = key.in_betweens.get(shape.name)
                        return data is not None and data.active is not None
        return False

    def execute(self, context: 'Context') -> Set[str]:
        key = context.object.active_shape_key.id_data
        identifier = self.identifier
        hero: 'InBetweens'
        item: 'InBetween'

        for hero in key.in_betweens:
            item = hero.search(identifier)
            if item is not None:
                break

        if item is None:
            self.report({'ERROR'}, "Unable to find in-between")
            return {'CANCELLED'}

        shape = key.key_blocks.get(hero.name)
        if shape is None:
            self.report({'ERROR'}, f'Hero shape key "{hero.name}" not found.')

        self.execute__internal__(hero, item, shape)
        return {'FINISHED'}

    def execute__internal__(self, _0: 'InBetweens', _1: 'InBetween', _2: 'ShapeKey') -> None:
        raise NotImplementedError((f'{self.__class__.__name__}.'
                                   f'execute__internal__(hero, inbetween, shapekey)'))


class INBETWEEN_OT_activate(ActivationValue, Operator):
    bl_idname = 'in_between.activate'
    bl_label = "Activate In-Between"
    bl_description = "Set the hero shape key value to the activation value of the in-between"
    bl_options = {'INTERNAL', 'UNDO'}

    def execute__internal__(self, _: 'InBetweens',
                            inbetween: 'InBetween',
                            shapekey: 'ShapeKey') -> None:
        shapekey.value = inbetween.activation_value


class INBETWEEN_OT_activation_value_update(ActivationValue, Operator):
    bl_idname = 'in_between.activation_value_update'
    bl_label = "Update Activation Value"
    bl_description = "Set the in-between activation value to the hero value"

    def execute__internal__(self, _: 'InBetweens',
                            inbetween: 'InBetween',
                            shapekey: 'ShapeKey') -> None:
        inbetween.activation_value = shapekey.value


class INBETWEEN_OT_activation_value_actions(ActivationValue, Operator):
    bl_idname = "in_between.activation_value_menu"
    bl_label = "Activation Value Actions"

    def execute(self, context: 'Context') -> Set[str]:

        identifier = self.identifier

        def draw(self, _: 'Context') -> None:
            layout = self.layout

            layout.operator(INBETWEEN_OT_activate.bl_idname,
                            text="Paste To Hero Value",
                            icon='EXPORT').identifier = identifier

            layout.operator(INBETWEEN_OT_activation_value_update.bl_idname,
                            text="Copy From Hero Value",
                            icon='IMPORT').identifier = identifier

        context.window_manager.popup_menu(draw)
        return {'FINISHED'}
