
from typing import Dict, List, Tuple, TYPE_CHECKING
import bpy
from ..lib.symmetry import symmetrical_split
if TYPE_CHECKING:
    from bpy.types import AnimData, Key
    from ..api.in_between import InBetween
    from ..api.in_betweens import InBetweens

MESSAGE_BROKER = object()

def datamap(key: 'Key') -> Dict[str, Tuple['InBetween', 'InBetweens']]:
    data = {}
    for hero in key.in_betweens:
        for item in hero:
            data[item.identifier] = (item, hero)
    return data


def changelog(animdata: 'AnimData',
              data: Dict[str, Tuple['InBetween', 'InBetweens']]
              ) -> Dict['InBetweens', List['InBetween']]:
    clog = {}
    for fc in animdata.drivers:
        vars = fc.driver.variables
        if len(vars) == 2:
            k = vars[0].name
            if k.startswith("inbetween_") and k in data:
                item, hero = data[k]
                item_name = item["name"] = fc.data_path[12:-8]
                hero_name = hero["name"] = vars[1].targets[0].data_path[12:-8]

                hpfix, hbase, hsfix = symmetrical_split(hero_name)
                ipfix, ibase, isfix = symmetrical_split(item_name)

                if not ibase.startswith(hbase) or ipfix != hpfix or isfix != hsfix:
                    clog.setdefault(hero, []).append(item)
    return clog


def update_shape_key_names(key: 'Key', clog: Dict[str, Tuple['InBetween', 'InBetweens']]) -> None:
    kbs = key.key_blocks
    for hero, items in clog.items():
        pfix, base, sfix = symmetrical_split(hero.name)
        for item in items:
            kb = kbs.get(item.name)
            if kb is not None:
                kb.name = item["name"] = f'{pfix}{base}_{item.activation_value:.3f}{sfix}'


def shape_key_name_callback():
    for key in bpy.data.shape_keys:
        if key.is_property_set("in_betweens"):
            animdata = key.animation_data
            if animdata:
                data = datamap(key)
                if data:
                    clog = changelog(animdata, data)
                    while clog:
                        update_shape_key_names(key, clog)
                        clog = changelog(animdata, data)
                        


@bpy.app.handlers.persistent
def enable_message_broker(_=None) -> None:
    bpy.msgbus.clear_by_owner(MESSAGE_BROKER)
    bpy.msgbus.subscribe_rna(key=(bpy.types.ShapeKey, "name"),
                             owner=MESSAGE_BROKER,
                             args=tuple(),
                             notify=shape_key_name_callback)
