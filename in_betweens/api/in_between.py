
from typing import Optional, TYPE_CHECKING
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, FloatProperty, PointerProperty, StringProperty
from .activation_curve import ActivationCurve, activation_curve_offset_update
from ..lib.driver_utils import driver_ensure
from ..lib.curve_mapping import keyframe_points_assign, to_bezier
from ..lib.symmetry import symmetrical_split
if TYPE_CHECKING:
    from bpy.types import Context


def inbetween_activation_range_min(inbetween: 'InBetween') -> float:
    return inbetween.get("activation_range_min", 0.0)


def inbetween_activation_range_min_set(inbetween: 'InBetween', value: float) -> None:
    armin = min(max(-10.0, min(value, inbetween_activation_value(inbetween) - 0.1)), 9.9)
    if armin != inbetween_activation_range_min(inbetween):
        inbetween["activation_range_min"] = armin

        armax = inbetween_activation_range_max(inbetween)
        if armax <= armin + 0.1:
            armax = armin + 0.1
            inbetween["activation_range_max"] = armax

        value = inbetween_activation_value(inbetween)
        activation_curve_offset_update(inbetween.activation_curve, armin, armax, value)


def inbetween_activation_range_max(inbetween: 'InBetween') -> float:
    return inbetween.get("activation_range_max", 1.0)


def inbetween_activation_range_max_set(inbetween: 'InBetween', value: float) -> None:
    armax = min(max(-9.9, max(value, inbetween_activation_value(inbetween) + 0.1)), 10.0)
    if armax != inbetween_activation_range_max(inbetween):
        inbetween["activation_range_max"] = armax

        armin = inbetween_activation_range_min(inbetween)
        if armin >= armax - 0.1:
            armin = armax - 0.1
            inbetween["activation_range_min"] = armin

        value = inbetween_activation_value(inbetween)
        activation_curve_offset_update(inbetween.activation_curve, armin, armax, value)


def inbetween_activation_value(inbetween: 'InBetween') -> float:
    armin = inbetween_activation_range_min(inbetween)
    armax = inbetween_activation_range_max(inbetween)
    ardif = armax - armin
    return inbetween.get("activation_value", armin + ardif * 0.5)


def inbetween_activation_value_set(inbetween: 'InBetween', value: float) -> None:
    armin = inbetween_activation_range_min(inbetween)
    armax = inbetween_activation_range_max(inbetween)
    value = min(max(armin + 0.1, value), armax - 0.1)

    if value != inbetween_activation_value(inbetween):
        inbetween["activation_value"] = value
        activation_curve_offset_update(inbetween.activation_curve, armin, armax, value)

        key = inbetween.id_data
        hero = key.key_blocks.get(next((x.name for x in key.in_betweens if any((i == inbetween for i in x.data))), ""))
        
        if hero is not None:
            pfix, base, sfix = symmetrical_split(hero.name)
            target = key.key_blocks.get(inbetween.name)
            if target is not None:
                target.name = f'{pfix}{base}_{value:.3f}{sfix}'


def inbetween_identifier(inbetween: 'InBetween') -> str:
    return inbetween.get("identifier", "")


def inbetween_is_valid(inbetween: 'InBetween') -> bool:
    return inbetween.name in inbetween.id_data.key_blocks


class InBetween(PropertyGroup):
    """Manages and stores settings for an in-between shape key"""

    def update(self, _: Optional['Context']=None) -> None:
        fcurve = driver_ensure(self.id_data, f'key_blocks["{self.name}"].value')
        fcurve.mute = self.mute

        points = self.activation_curve.curve.points
        xrange = (inbetween_activation_range_min(self), inbetween_activation_range_max(self))
        yrange = (0.0, self.value)
        points = to_bezier(points, xrange, yrange, extrapolate=False)
        
        keyframe_points_assign(fcurve.keyframe_points, points)

    activation_value: FloatProperty(
        name="Activation Value",
        description="The value of the shape key around which the in-between is activated",
        min=-10.0,
        max=10.0,
        soft_min=0.0,
        soft_max=1.0,
        get=inbetween_activation_value,
        set=inbetween_activation_value_set,
        precision=3,
        options=set(),
        )

    activation_curve: PointerProperty(
        name="Curve",
        description="In-Between interpolation curve",
        type=ActivationCurve,
        options=set(),
        update=update
        )

    value: FloatProperty(
        name="Value",
        description="The value of the in-between when fully activated",
        min=0.0,
        max=10.0,
        soft_min=0.1,
        soft_max=1.0,
        default=1.0,
        precision=3,
        options=set(),
        update=update
        )

    identifier: StringProperty(
        name="Shape",
        description="Unique identifier used to hold a reference to the in-between shape key (read-only)",
        get=inbetween_identifier,
        options={'HIDDEN'}
        )

    is_valid: BoolProperty(
        name="Valid",
        description="Whether the in-between targets an extant shape key (read-only)",
        get=inbetween_is_valid,
        options=set()
        )

    mute: BoolProperty(
        name="Mute",
        description=("Whether or not the in-between shape key's driver is enabled. Disabling "
                     "the driver allows (temporary) editing of the shape key's value in the UI"),
        default=False,
        options=set(),
        update=update
        )

    activation_range_min: FloatProperty(
        name="Activation Min",
        description="Lower bounds for in-between activation",
        min=-10.0,
        max=9.999,
        get=inbetween_activation_range_min,
        set=inbetween_activation_range_min_set,
        options=set(),
        )

    activation_range_max: FloatProperty(
        name="Activation Max",
        description="Upper bounds for in-between activation",
        min=-9.999,
        max=10.0,
        get=inbetween_activation_range_max,
        set=inbetween_activation_range_max_set,
        options=set(),
        )
