
from typing import TYPE_CHECKING, Tuple
from bpy.types import PropertyGroup
from bpy.props import FloatProperty
from in_betweens.lib.symmetry import symmetrical_split
from ..lib.curve_mapping import BCLMAP_CurveManager
if TYPE_CHECKING:
    from .in_between import InBetween


def activation_range_min(activation: 'InBetweenActivation') -> float:
    return activation.get("range_min", 0.0)


def activation_range_min_set(activation: 'InBetweenActivation', value: float) -> None:
    cval = activation.center
    rmin = min(max(-10.0, min(value, cval - 0.1)), 9.9)
    if rmin != activation.range_min:
        activation["range_min"] = rmin
        rmax = activation.range_max
        if rmax <= rmin + 0.1:
            rmax = rmin + 0.1
            activation["range_max"] = rmax
        activation.in_between.update()


def activation_range_max(activation: 'InBetweenActivation') -> float:
    return activation.get("range_max", 1.0)


def activation_range_max_set(activation: 'InBetweenActivation', value: float) -> None:
    cval = activation.center
    rmax = min(max(-9.9, max(value, cval + 0.1)), 10.0)
    if rmax != activation.range_max:
        activation["range_max"] = rmax
        rmin = activation.range_min
        if rmin >= rmax - 0.1:
            rmin = rmax - 0.1
            activation["range_min"] = rmin
        activation.in_between.update()


def activation_center(activation: 'InBetweenActivation') -> float:
    rmin = activation.range_min
    rmax = activation.range_max
    rdif = rmax - rmin
    return activation.get("center", rmin + rdif * 0.5)


def activation_center_set(activation: 'InBetweenActivation', value: float) -> None:
    rmin = activation.range_min
    rmax = activation.range_max
    cval = min(max(rmin + 0.1, value), rmax - 0.1)
    if cval != activation.center:
        activation["center"] = cval
        ibtw = activation.in_between
        hero = ibtw.hero
        pfix, base, sfix = symmetrical_split(hero.name)
        ibkb = ibtw.id_data.key_blocks.get(ibtw.name)
        if ibkb is not None:
            ibkb.name = f'{pfix}{base}_{cval:.3f}{sfix}'


def activation_target_update_handler(activation: 'InBetweenActivation', _) -> None:
    activation.in_between.update()


class InBetweenActivation(BCLMAP_CurveManager, PropertyGroup):

    center: FloatProperty(
        name="Center",
        description="The value of the shape key around which the in-between is activated",
        min=-10.0,
        max=10.0,
        soft_min=0.0,
        soft_max=1.0,
        get=activation_center,
        set=activation_center_set,
        precision=3,
        options=set(),
        )

    @property
    def in_between(self) -> 'InBetween':
        path: str = self.path_from_id()
        return self.id_data.path_resolve(path.rpartition(".activation")[0])

    range_min: FloatProperty(
        name="Activation Min",
        description="Lower bounds for in-between activation",
        min=-10.0,
        max=9.999,
        get=activation_range_min,
        set=activation_range_min_set,
        options=set(),
        )

    range_max: FloatProperty(
        name="Activation Max",
        description="Upper bounds for in-between activation",
        min=-9.999,
        max=10.0,
        get=activation_range_max,
        set=activation_range_max_set,
        options=set(),
        )

    target: FloatProperty(
        name="Target",
        description="The value of the in-between when fully activated",
        min=0.0,
        max=10.0,
        soft_min=0.1,
        soft_max=1.0,
        default=1.0,
        precision=3,
        options=set(),
        update=activation_target_update_handler
        )

    def update(self) -> None:
        super().update()
        self.in_between.update()
