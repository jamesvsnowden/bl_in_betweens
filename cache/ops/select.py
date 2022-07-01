
from typing import Set, TYPE_CHECKING
from uuid import uuid4
from bpy.types import Operator
from bpy.props import CollectionProperty, StringProperty
from .base import Base
from ..api.in_between import InBetween
from ..api.target import Target
from ..lib.driver_utils import driver_ensure, driver_find
if TYPE_CHECKING:
    from bpy.types import Context, Event


class INBETWEEN_OT_select(Base, Operator):
    
    bl_idname = 'in_between.select'
    bl_label = "Select In-Between"
    bl_description = "Select a shape key to add as an in-between"
    bl_options = {'INTERNAL', 'UNDO'}

    targets: CollectionProperty(
        name="Targets",
        type=Target,
        options=set()
        )

    target: StringProperty(
        name="Target",
        default="",
        options=set()
        )

    def invoke(self, context: 'Context', _: 'Event') -> Set[str]:
        object = context.object
        hero = object.active_shape_key
        key = hero.id_data
        ref = object.reference_key

        targets = self.targets
        targets.clear()

        for shape in key.key_blocks:
            if (shape != hero
                and shape != ref
                and not driver_find(key, f'key_blocks["{shape.name}"].value')
                ):
                targets.add().name = shape.name

        self.target = ""
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, _: 'Context') -> None:
        self.layout.prop_search(self, "target", self, "targets", icon='SHAPEKEY_DATA', text="")

    def execute(self, context: 'Context') -> Set[str]:
        object = context.object
        hero = object.active_shape_key
        key = hero.id_data
        target = key.key_blocks.get(self.target)

        if target:
            inbetweens = key.in_betweens.get(hero.name)
            if inbetweens is None:
                inbetweens = key.in_betweens.add()
                inbetweens["name"] = hero.name

            inbtwn: InBetween = inbetweens.data.add()
            inbtwn["name"] = target.name
            inbtwn["activation_value"] = hero.value
            inbtwn["activation_radius"] = 1.0-hero.value
            inbtwn.activation_curve.__init__(type='BELL',
                                             ramp='HEAD',
                                             interpolation='QUAD',
                                             easing='EASE_IN_OUT')

            fcurve = driver_ensure(key, f'key_blocks["{target.name}"].value')
            driver = fcurve.driver
            driver.type = 'SCRIPTED'
            driver.expression = "var"

            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = inbtwn.identifier
            var.targets[0].id_type = 'KEY'
            var.targets[0].id = key
            var.targets[0].data_path = 'reference_key.value'

            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = "var"
            var.targets[0].id_type = 'KEY'
            var.targets[0].id = key
            var.targets[0].data_path = f'key_blocks["{hero.name}"].value'

            inbtwn.update()
            inbetweens.active_index = len(inbetweens)-1

        return {'FINISHED'}