
from bpy.types import PropertyGroup
from ..lib.curve_mapping import BCLMAP_CurveManager


def activation_curve_offset_update(curve: 'ActivationCurve',
                                   armin: float,
                                   armax: float,
                                   value: float) -> None:
    curve.offset = (((value - armin) * 2.0) / (armax - armin)) + -1.0


class ActivationCurve(BCLMAP_CurveManager, PropertyGroup):

    def update(self) -> None:
        super().update()
        self.id_data.path_resolve(self.path_from_id().rpartition(".")[0]).update()
