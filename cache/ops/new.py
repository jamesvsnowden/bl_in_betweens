
from typing import Set, TYPE_CHECKING
from bpy.types import Operator
from ..lib.asks import COMPAT_ENGINES, COMPAT_OBJECTS
if TYPE_CHECKING:
    from bpy.types import Context


class INBETWEEN_OT_new(Operator):
    
    bl_idname = 'in_between.new'
    bl_label = "New In-Between"
    bl_description = "Add a new in-between shape key"
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        if context.engine in COMPAT_ENGINES:
            object = context.object
            if object is not None and object.type in COMPAT_OBJECTS:
                shape = object.active_shape_key
                return shape is not None and shape != shape.id_data.reference_key
        return False

    def execute(self, context: 'Context') -> Set[str]:
        hero = context.object.active_shape_key
        hero.id_data.in_betweens.new(hero)
        return {'FINISHED'}
