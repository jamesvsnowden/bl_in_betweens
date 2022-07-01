
from ..lib.symmetry import symmetrical_split


def inbetween_name_format(heroname: str, center: float) -> str:
    pfix, base, sfix = symmetrical_split(heroname)
    return f'{pfix}{base}_{center:.3f}{sfix}'