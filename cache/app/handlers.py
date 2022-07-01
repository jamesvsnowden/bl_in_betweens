
from typing import TYPE_CHECKING, Optional, Union
from bpy.types import Key
import bpy
if TYPE_CHECKING:
    from bpy.types import FCurve, ShapeKey
    from ..api.hero import InBetweenHero
    from ..api.in_between import InBetween

_owners = {}
_locks = {}


def find_inbetween_value_driver(key: Key, inbetween_id: str) -> Optional['FCurve']:
    animdata = key.animation_data
    if animdata is not None:
        varname = f'inbetweens_{inbetween_id}'
        for fcurve in animdata.drivers:
            if fcurve.driver.variables.get(varname) is not None:
                return fcurve


def get_hero_shape_key_name(fcurve: 'FCurve') -> Optional[str]:
    variable = fcurve.driver.variables.get("hero_value")
    if variable is not None and variable.type == 'SINGLE_PROP':
        target = variable.targets[0]
        if target.id_type == 'KEY':
            key = target.id
            if isinstance(key, Key) and key == fcurve.id_data:
                path = variable.targets[0].data_path
                if path.startswith('key_blocks["') and path.endswith('"].value'):
                    name = path[12:-8]
                    if name in key.key_blocks:
                        return name


def on_in_between_name_update(id: str) -> None:
    if _locks.get(id, False):
        return
    for key in bpy.data.shape_keys:
        if key.is_property_set("in_betweens") :
            inbetween = key.in_betweens.search(id)
            if inbetween is not None:
                fcurve = find_inbetween_value_driver(key, inbetween.identifier)
                if fcurve is not None:
                    name = get_hero_shape_key_name(fcurve)
                    if name:
                        try:
                            shape = key.path_resolve(fcurve.data_path)
                        except ValueError:
                            pass
                        else:
                            _locks[id] = True
                            shape.name = format_inbetween_name(inbetween, name)
                            del _locks[id]



def on_hero_name_update(id: str) -> None:
    for key in bpy.data.shape_keys:
        if key.is_property_set("in_betweens"):
            hero = key.in_betweens.heros.search(id)
            if hero is not None:
                inbetweens = hero.in_betweens
                if inbetweens:
                    fcurve = find_inbetween_value_driver(key, inbetweens[0].identifier)
                    if fcurve is not None:
                        name = get_hero_shape_key_name(fcurve)
                        if name:
                            shape = key.key_blocks.get(name)
                            if shape is not None:
                                for inbetween in inbetweens:
                                    shape = key.key_blocks.get(inbetween.name)
                                    if shape is not None:
                                        _locks[inbetween.identifier] = True
                                        shape.name = format_inbetween_name(inbetween, name)
                                _locks.clear()
            return


def subscribe_to_hero_name_updates(hero: 'InBetweenHero') -> None:
    bpy.msgbus.subscribe(key=hero.id_data.key_blocks[hero.name].path_resolve("name", False),
                         owner=_owners.setdefault(hero.identifier, object()),
                         args=(hero.identifier,),
                         notify=on_hero_name_update)


def subscribe_to_inbetween_name_updates(inbetween: 'InBetween') -> None:
    bpy.msgbus.subscribe(key=inbetween.id_data.key_blocks[inbetween.name].path_resolve("name", False),
                         owner=_owners.setdefault(inbetween.identifier, object()),
                         args=(inbetween.identifier,),
                         notify=on_in_between_name_update)

def observers_init(component: Union['InBetween', 'InBetweenHero']) -> None:
