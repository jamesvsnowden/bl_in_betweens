
from typing import List, Optional, Tuple, Union
from bpy.types import Object, PropertyGroup, ShapeKey
from bpy.props import CollectionProperty, IntProperty, PointerProperty
from in_betweens.app.drivers import inbetween_value_driver_init
from in_betweens.lib.driver_utils import driver_ensure, driver_remove
from in_betweens.lib.symmetry import symmetrical_split
from in_betweens.ops.base import COMPAT_OBJECTS
from ..lib.asks import ASKSNamespace, add_proxy_variable
from ..app.utils import inbetween_name_format
from .hero import InBetweenHero
from .heros import InBetweenHeros
from .in_between import InBetween

class InBetweens(ASKSNamespace, PropertyGroup):

    collection__internal__: CollectionProperty(
        name="In-Betweens",
        type=InBetween,
        options=set()
        )

    heros: PointerProperty(
        name="Heros",
        description="Collection of hero shape key data",
        type=InBetweenHeros,
        options=set()
        )

    def __getitem__(self, key: Union[int, str, slice, 'ShapeKey', InBetweenHero]) -> Union[InBetween, List[InBetween]]:
        if isinstance(key, InBetweenHero):
            res = []
            hid = key.identifier
            for ibtw in self:
                if ibtw.get("hero", "") == hid:
                    res.append(ibtw)
            return res
        return super()[key]

    def new(self, hero: ShapeKey, shape: Optional[ShapeKey]=None) -> InBetween:

        if not isinstance(hero, ShapeKey):
            raise TypeError((f'{self.__class__.__name__}.new(hero, shape=None): '
                             f'Expected hero to be ShapeKey, not {hero.__class__.__name__}'))

        if shape is not None and not isinstance(shape, ShapeKey):
            raise TypeError((f'{self.__class__.__name__}.new(hero, shape=None): '
                             f'Expected shape to be ShapeKey, not {shape.__class__.__name__}'))

        if hero.id_data != self.id_data:
            raise TypeError((f'{self.__class__.__name__}.new(hero, shape=None): '
                             f'hero is from another Key'))

        key = self.id_data

        import bpy
        for object in bpy.data.objects:
            if object.type in COMPAT_OBJECTS and object.data == key.user: break

        heros = self.heros

        if hero in heros:
            hero_id = heros[hero].identifier
        else:
            _hero = heros.collection__internal__.add()
            _hero["name"] = hero.name
            hero_id = _hero.identifier
            key.asks.notify('INBETWEENS::HERO_CREATED', hero.name)
        
        range_min = hero.slider_min
        range_max = hero.slider_max
        range_dif = (range_max - range_min) * 0.5

        if range_dif < 0.2:
            range_min -= 0.1 - range_dif
            range_max += 0.1 - range_dif

        center = hero.value
        center = center if center - range_min >= 0.1 else range_min + range_dif

        name = inbetween_name_format(hero.name, center)

        if shape is None:
            shape = object.shape_key_add(name=name, from_mix=False)
        else:
            # TODO diff shape with hero
            shape.name = name
        
        inbetween: 'InBetween' = self.collection__internal__.add()
        inbetween["hero"] = hero_id
        inbetween["name"] = name

        inbetween_value_driver_init(inbetween, hero.name)

        activation = inbetween.activation
        activation["center"] = center
        activation["target"] = 1.0
        activation["range_min"] = range_min
        activation["range_max"] = range_max
        #TODO move to curve_mapping utility function
        activation.__init__(type='BELL', ramp='HEAD', interpolation='QUAD', easing='EASE_IN_OUT')

        inbetween.update()

        shapes = key.key_blocks
        a_index = object.active_shape_key_index
        i_index = shapes.find(inbetween.name)
        h_index = shapes.find(hero.name)
        offset = i_index - h_index - 1

        object.active_shape_key_index = i_index

        while offset:
            bpy.ops.object.shape_key_move(type='UP')
            offset -= 1

        object.active_shape_key_index = a_index

        key.asks.notify('INBETWEENS::INBETWEEN_CREATED', shape.name, hero=hero.name)
        return inbetween

    def remove(self, inbetween: InBetween, remove_shape_key: Optional[bool]=False) -> None:
        
        if not isinstance(inbetween, InBetween):
            raise TypeError((f'{self.__class__.__name__}.remove(inbetween, remove_shape_key=False): '
                             f'Expected inbetween to be InBetween, not {inbetween.__class__.__name__}'))

        key = self.id_data

        if inbetween.id_data != key:
            raise ValueError((f'{self.__class__.__name__}.remove(inbetween, remove_shape_key=False): '
                             f'inbetween is not a member of this collection'))

        hero = inbetween.hero
        data = self.collection__internal__
        name = inbetween.name

        key.asks.notify('INBETWEENS::INBETWEEN_DISPOSE', name, hero=hero.name)
        driver_remove(key, f'key_blocks["{name}"].value')
        data.remove(data.find(name))
        key.asks.notify('INBETWEENS::INBETWEEN_REMOVED', name, hero=hero.name)

        if len(hero.in_betweens) == 0:
            hname = hero.name
            key.asks.notify("INBETWEENS::HERO_DISPOSE", hname)
            heros = self.heros
            heros.collection__internal__.remove(heros.find(hname))
            key.asks.notify("INBETWEENS::HERO_REMOVED", hname)

        if remove_shape_key:
            import bpy
            usr = key.user
            for obj in bpy.data.objects:
                if obj.type in COMPAT_OBJECTS and obj.data == usr: break

            kbs = key.key_blocks
            idx = kbs.find(name)

            if idx >= 0:
                key.asks.notify("INBETWEENS::SHAPEKEY_DISPOSE", name)
                obj.shape_key_remove(kbs[idx])
                key.asks.notify("INBETWEENS::SHAPEKEY_REMOVED", name)
