
from typing import Optional, Tuple, Union, TYPE_CHECKING
from ..lib.curve_mapping import draw_curve_manager_ui
from ..ops.activate import INBETWEEN_OT_activate
if TYPE_CHECKING:
    from bpy.types import UILayout
    from ..api.in_between import InBetween


def layout_split(layout: 'UILayout',
                 label: Optional[str]="",
                 align: Optional[bool]=False,
                 factor: Optional[float]=0.385,
                 decorate: Optional[bool]=True,
                 decorate_fill: Optional[bool]=True
                 ) -> Union['UILayout', Tuple['UILayout', ...]]:
    split = layout.row().split(factor=factor)
    col_a = split.column(align=align)
    col_a.alignment = 'RIGHT'
    if label:
        col_a.label(text=label)
    row = split.row()
    col_b = row.column(align=align)
    if decorate:
        col_c = row.column(align=align)
        if decorate_fill:
            col_c.label(icon='BLANK1')
        else:
            return col_a, col_b, col_c
    return col_b if label else (col_a, col_b)


def draw_inbetween_settings(layout: 'UILayout', settings: 'InBetween') -> None:

    labels, values, decorations = layout_split(layout, decorate_fill=False)
    labels.label(text="Activation  Value")
    values.prop(settings, "activation_value", text="")
    decorations.operator(INBETWEEN_OT_activate.bl_idname,
                         text="",
                         icon='ZOOM_SELECTED').identifier = settings.identifier

    labels, values = layout_split(layout, align=True)
    labels.label(text="Activation Range Min")
    labels.label(text="Max")
    values.prop(settings, "activation_range_min", text="")
    values.prop(settings, "activation_range_max", text="")

    labels, values = layout_split(layout, decorate=False)
    labels.label(text="Activation Curve")
    draw_curve_manager_ui(values, settings.activation_curve)
    layout_split(layout, label="Target Value").prop(settings, "value", text="")