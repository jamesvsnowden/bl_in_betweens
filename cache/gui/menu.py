
from typing import TYPE_CHECKING
from bpy.types import Menu
from ..ops.new import INBETWEEN_OT_new
from ..ops.select import INBETWEEN_OT_select
if TYPE_CHECKING:
    from bpy.types import Context


def draw_menu_items(menu: 'Menu', context: 'Context') -> None:
    object = context.object
    if object is not None:
        shape = object.active_shape_key
        if shape is not None:
            key = shape.id_data
            if shape != key.reference_key:
                layout = menu.layout
                layout.separator()
                layout.operator(INBETWEEN_OT_new.bl_idname,
                                icon='ADD',
                                text="New In-Between")
                layout.operator(INBETWEEN_OT_select.bl_idname,
                                icon='ANIM',
                                text="Select In-Between")
