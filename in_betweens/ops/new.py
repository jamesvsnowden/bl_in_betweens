
from typing import Set, TYPE_CHECKING
from uuid import uuid4
from bpy.types import Operator
from .base import Base
from ..lib.symmetry import symmetrical_split
from ..lib.driver_utils import driver_ensure
if TYPE_CHECKING:
    from bpy.types import Context
    from ..api.in_between import InBetween


class INBETWEEN_OT_new(Base, Operator):
    
    bl_idname = 'in_between.new'
    bl_label = "New In-Between"
    bl_description = "Add a new in-between shape key"
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context: 'Context') -> Set[str]:
        object = context.object
        hero = object.active_shape_key
        key = hero.id_data

        inbetweens = key.in_betweens.get(hero.name)

        if inbetweens is None:
            inbetweens = key.in_betweens.add()
            inbetweens["name"] = hero.name

        amin = hero.slider_min
        amax = hero.slider_max

        rdif = (amax - amin) * 0.5
        if rdif < 0.2:
            amin -= 0.1 - rdif
            amax += 0.1 - rdif

        hval = hero.value
        aval = hval if hval - amin >= 0.1 else amin + rdif

        p, k, s = symmetrical_split(hero.name)
        target = object.shape_key_add(name=f'{p}{k}_{aval:.3f}{s}', from_mix=False)

        inbtwn: InBetween = inbetweens.data.add()
        inbtwn["name"] = target.name
        inbtwn["identifier"] = f'inbetween_{uuid4().hex}'
        inbtwn["value"] = 1.0
        inbtwn["activation_value"] = aval
        inbtwn["activation_range_min"] = amin
        inbtwn["activation_range_max"] = amax
        inbtwn.activation_curve.__init__(type='BELL',
                                         ramp='HEAD',
                                         interpolation='QUAD',
                                         easing='EASE_IN_OUT',
                                         offset=(((aval - amin) * 2.0) / (amax - amin)) + -1.0)

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

        shapes = object.data.shape_keys.key_blocks
        i_item = shapes.find(target.name)
        i_hero = shapes.find(hero.name)
        offset = i_item - i_hero - 1

        import bpy
        object.active_shape_key_index = i_item
        while offset:
            bpy.ops.object.shape_key_move(type='UP')
            offset -= 1
        object.active_shape_key_index = i_hero

        return {'FINISHED'}
