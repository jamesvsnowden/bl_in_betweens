
from bpy.types import PropertyGroup
from bpy.props import CollectionProperty
from ..lib.asks import ASKSNamespace
from .hero import InBetweenHero


class InBetweenHeros(ASKSNamespace, PropertyGroup):

    collection__internal__: CollectionProperty(
        type=InBetweenHero,
        options={'HIDDEN'}
        )

    