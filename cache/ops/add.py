
from typing import Set, TYPE_CHECKING
from bpy.types import Operator
from ..lib.asks import COMPAT_ENGINES, COMPAT_OBJECTS
from .new import INBETWEEN_OT_new
from .select import INBETWEEN_OT_select
if TYPE_CHECKING:
    from bpy.types import Context

class INBETWEEN_OT_add(Operator):
    
    bl_idname = 'in_betweens.inbetween_add'
    bl_label = "Add In-Between"
    bl_description = "Add an in-between"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context: 'Context') -> bool:
        if context.engine in COMPAT_ENGINES:
            object = context.object
            if object is not None and object.type in COMPAT_OBJECTS:
                shape = object.active_shape_key
                return shape is not None and shape != shape.id_data.reference_key
        return False

    def draw(self, _: 'Context') -> None:
        layout = self.layout
        layout.operator(INBETWEEN_OT_new.bl_idname, icon='ADD', text="New In-Between")
        layout.operator(INBETWEEN_OT_select.bl_idname, icon='ANIM', text="Select In-Between")

    def execute(self, context: 'Context') -> Set[str]:
        context.window_manager.popup_menu(INBETWEEN_OT_add.draw)
        return {'FINISHED'}
