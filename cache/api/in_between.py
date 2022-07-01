
from typing import Optional, TYPE_CHECKING, Tuple
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, PointerProperty
from ..lib.asks import ASKSComponent
from ..lib.driver_utils import driver_ensure, driver_find
from ..lib.curve_mapping import keyframe_points_assign, to_bezier
from .activation import InBetweenActivation
if TYPE_CHECKING:
    from .hero import InBetweenHero


def inbetween_is_valid(inbetween: 'InBetween') -> bool:
    return inbetween.name in inbetween.id_data.key_blocks


def inbetween_mute_update_handler(inbetween: 'InBetween', _) -> None:
    fc = driver_find(inbetween.id_data, f'key_blocks["{inbetween.name}"].value')
    if fc:
        fc.mute = inbetween.mute


class InBetween(ASKSComponent, PropertyGroup):
    """Manages and stores settings for an in-between shape key"""

    activation: PointerProperty(
        name="Activation",
        description="In-Between activation settings",
        type=InBetweenActivation,
        options=set()
        )

    @property
    def hero(self) -> Optional['InBetweenHero']:
        return self.id_data.in_betweens.heros.search(self.get("hero", ""))

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
        update=inbetween_mute_update_handler
        )

    show_expanded: BoolProperty(
        name="Expand",
        description="Show in-between settings in the UI",
        default=False,
        options=set()
        )
        

    def update(self) -> None:
        fc = driver_ensure(self.id_data, f'key_blocks["{self.name}"].value')
        fc.mute = self.mute

        act = self.activation
        pts = to_bezier(act.curve.points,
                        x_range=(act.range_min, act.range_max),
                        y_range=(0.0, act.target),
                        extrapolate=False)
    
        keyframe_points_assign(fc.keyframe_points, pts)
