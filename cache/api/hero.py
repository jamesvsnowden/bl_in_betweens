
from typing import List, TYPE_CHECKING
from bpy.types import PropertyGroup
from ..lib.asks import ASKSComponent
if TYPE_CHECKING:
    from bpy.types import ShapeKey
    from .in_between import InBetween

class InBetweenHero(ASKSComponent, PropertyGroup):

    @property
    def in_betweens(self) -> List['InBetween']:
        id = self.identifier
        return [x for x in self.id_data.in_betweens if x.get("hero", "") == id]

    def __init__(self, shape: 'ShapeKey') -> None:
        self["name"] = shape.name