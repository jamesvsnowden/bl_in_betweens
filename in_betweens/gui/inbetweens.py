
from typing import TYPE_CHECKING
from bpy.types import UIList
if TYPE_CHECKING:
    from bpy.types import UILayout
    from ..api.in_between import InBetween


class INBETWEENS_UL_inbetweens(UIList):

    def draw_item(self, _0,
                  layout: 'UILayout', _1,
                  item: 'InBetween', _2, _3, _4, _5, _6) -> None:

        shape = item.id_data.key_blocks.get(item.name)

        row = layout.row()
        row.alert = shape is None
        row.label(icon='SHAPEKEY_DATA', text=item.name)

        if shape:
            row = row.row()
            row.emboss = 'NONE_OR_STATUS'
            row.alignment = 'RIGHT'
            row.prop(shape, "value", text="")
