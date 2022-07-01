# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "In-Betweens",
    "description": "In-between shape keys.",
    "author": "James Snowden",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Properties > data",
    "doc_url": "https://jamesvsnowden.github.io/bl_in_betweens/",
    "tracker_url": "https://github.com/jamesvsnowden/bl_in_betweens/issues",
    "category": "Animation",
}

UPDATE_URL = ""

from typing import Set
import bpy
from .lib import asks


def draw_inbetween(layout: bpy.types.UILayout, entity: asks.types.Entity) -> None:
    components = entity.components
    components["owner"].draw(layout, label="Hero")
    components["range"].draw(layout)   
    components["curve"].draw(layout)
    components["value"].draw(layout)


class AddInBetween(bpy.types.Operator):

    bl_idname = "inbetweens.add"
    bl_label = "Add In-Between"
    bl_description = ""
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        if asks.utils.validate_context(context):
            object = context.object
            if object is not None and asks.utils.supports_shape_keys(object):
                shapekey = object.active_shape_key
                if shapekey is not None:
                    key = shapekey.id_data
                    if not key.use_relative or object.active_shape_key_index > 0:
                        entity = key.asks.entities.get(shapekey)
                        return entity is None or not entity.tag


class NewInBetween(bpy.types.Operator):

    bl_idname = "inbetweens.new"
    bl_label = "New In-Between"
    bl_description = ""
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        if asks.utils.validate_context(context):
            object = context.object
            if object is not None and asks.utils.supports_shape_keys(object):
                shapekey = object.active_shape_key
                if shapekey is not None:
                    key = shapekey.id_data
                    return not key.use_relative or object.active_shape_key_index > 0

    def execute(self, context: bpy.types.Context) -> Set[str]:
        object = context.object
        k_hero = object.active_shape_key
        system = k_hero.id_data.asks

        e_owner = system.entities.ensure(k_hero)
        c_owner = e_owner.shape()

        c_curve = system.components.create("inbetweens.curve",
                                           label="Curve")

        c_value = system.components.create("inbetweens.value",
                                           label="Target Value",
                                           value=1.0)

        c_range = system.components.create("inbetweens.range",
                                           min=k_hero.slider_min,
                                           max=k_hero.value,
                                           label="Range",
                                           label_min="Start",
                                           label_max="Finish")

        k_inbtw = object.shape_key_add(name=self.name, from_mix=False)
        e_inbtw = system.entities.create(k_inbtw, type="INBETWEEN", draw=draw_inbetween)
        e_inbtw.tags.add('INBETWEEN')

        e_inbtw.components.attach(c_owner, name="owner")
        e_inbtw.components.attach(c_curve, name="curve")
        e_inbtw.components.attach(c_range, name="range")
        e_inbtw.components.attach(c_value, name="value")

        e_inbtw.processors.assign(inbetween_rename, c_owner)
        e_inbtw.processors.assign(inbetween_driver_update, c_owner)
        e_inbtw.processors.assign(inbetween_fcurve_update, c_range, c_value, c_curve)

        e_owner.children.append(e_inbtw)

        inbetween_driver_update(e_inbtw, c_owner)
        inbetween_fcurve_update(e_inbtw, c_range, c_value, c_curve)

        return {'FINISHED'}


def inbetween_rename(e_inbetween: asks.types.Entity,
                     c_owner: asks.types.ShapeComponent,
                     c_range: asks.types.RangeComponent) -> None:
    k_inbetween = e_inbetween.shape().resolve()
    if k_inbetween:
        k_inbetween.name = f'{c_owner.value}_{c_range.max:.2f}'


def inbetween_fcurve_update(e_inbtw: asks.types.Entity,
                            c_range: asks.types.RangeComponent,
                            c_value: asks.types.ValueComponent,
                            c_curve: asks.types.CurveComponent) -> None:
    fcurve = e_inbtw.fcurve(True)
    points = c_curve.points.to_bezier(range_x=(c_range.min, c_range.max),
                                      range_y=(0.0, c_value.value),
                                      extrapolate=False)
    asks.utils.set_keyframe_points(fcurve, points)


def inbetween_driver_update(e_inbtw: asks.types.Entity,
                            c_owner: asks.types.ShapeComponent) -> None:
    driver = e_inbtw.driver(True)

    variables = driver.variables
    while len(variables):
        variables.remove(variables[-1])

    for param in e_inbtw.parameters:
        variable = variables.new()
        variable.type = 'SINGLE_PROP'
        variable.name = f'var_{str(len(variables)).zfill(3)}'

        target = variable.targets[0]
        target.id_type = 'KEY'
        target.id = e_inbtw.id_data
        target.data_path = param.data_path

    variable = variables.new()
    variable.type = 'SINGLE_PROP'
    variable.name = f'var_{str(len(variables)).zfill(3)}'

    target = variable.targets[0]
    target.id_type = 'KEY'
    target.id = e_inbtw.id_data
    target.data_path = f'key_blocks["{c_owner.value}"].value'

    driver.type = 'SCRIPTED'
    driver.expression = "*".join(variables.keys())


def register():
    ns = asks.utils.namespace("inbetweens")
    ns.add_component("value", asks.types.ValueComponent)
    ns.add_component("range", asks.types.RangeComponent)
    ns.add_component("curve", asks.types.CurveComponent)
    ns.add_draw_handler(draw_inbetween)
    ns.add_processor(inbetween_driver_update)
    ns.add_processor(inbetween_fcurve_update)
    ns.add_context_menu_item(NewInBetween)
    ns.register()


def unregister():
    asks.utils.namespace("inbetweens").unregister()
