
from typing import TYPE_CHECKING
from ..lib.driver_utils import driver_ensure, driver_variables_clear
if TYPE_CHECKING:
    from bpy.types import ShapeKey
    from ..api.hero import InBetweenHero
    from ..api.in_between import InBetween

HERO_VALUE_VARIABLE_NAME = "hero"


def value_data_path(shape_name: str) -> str:
    return f'key_blocks["{shape_name}"].value'


def proxy_variable_name(inbetween: 'InBetween') -> str:
    return f'inbetween_{inbetween.identifier}'


def inbetween_value_driver_init(inbetween: 'InBetween', heroname: str) -> None:
    fcurve = driver_ensure(inbetween.id_data, value_data_path(inbetween.name))
    driver = fcurve.driver

    variables = driver.variables
    driver_variables_clear(variables)

    names = (proxy_variable_name(inbetween),
             "i", "w", HERO_VALUE_VARIABLE_NAME)

    paths = ("reference_key.value",
             inbetween.influence_property_path,
             inbetween.weight_property_path,
             value_data_path(heroname))

    for name, path in zip(names, paths):
        variable = variables.new()
        variable.type = 'SINGLE_PROP'
        variable.name = name

        target = variable.targets[0]
        target.id_type = 'KEY'
        target.id = inbetween.id_data
        target.data_path = path

    driver.type = 'SCRIPTED'
    driver.expression = "*".join(names[1:])