
from typing import Any, Iterator, List, Optional, Union
from bpy.types import PropertyGroup
from bpy.props import CollectionProperty, IntProperty
from .in_between import InBetween

class InBetweens(PropertyGroup):

    active_index: IntProperty(
        name="In-Between",
        description="In-Between shape key",
        min=0,
        default=0,
        options=set()
        )

    @property
    def active(self) -> Optional[InBetween]:
        index = self.active_index
        return self[index] if index < len(self) else None

    data: CollectionProperty(
        name="In-Betweens",
        type=InBetween,
        options=set()
        )

    def __len__(self) -> int:
        return len(self.data)

    def __iter__(self) -> Iterator[InBetween]:
        return iter(self.data)

    def __getitem__(self, key: Union[int, str, slice]) -> Union[InBetween, List[InBetween]]:
        return self.data[key]

    def get(self, name: str, default: Any) -> Any:
        return self.data.get(name, default)

    def search(self, identifier: str) -> Optional[InBetween]:
        return next((item for item in self if item.identifier == identifier), None)
