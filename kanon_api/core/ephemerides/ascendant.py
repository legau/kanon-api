from kanon.units.radices import BasedQuantity

from kanon_api.units import degree

from .tables import ObliqueAscension, RightAscension
from .true_position import sun_true_pos
from .utils import mod


def ascendant(days: float, latitude: float) -> BasedQuantity:
    sun = sun_true_pos(round(days))

    hours_arc = (days - round(days)) * 24 * 15 * sun.unit

    sun_rising = ObliqueAscension.get(sun, latitude)
    sun_setting = ObliqueAscension.get(mod(sun.value + 180), latitude)

    diurnal_arc = mod(sun_setting - sun_rising)

    ascension_degree = mod(sun_rising + hours_arc + diurnal_arc / 2)

    return ObliqueAscension.reverse_get(ascension_degree, latitude)


def houses(ascendant: BasedQuantity, latitude: float) -> list[BasedQuantity]:

    a0 = ObliqueAscension.get(ascendant, latitude)
    a1 = RightAscension.get(ascendant)
    a10 = mod(a0 - 90 * degree)
    a7 = mod(a1 + 180 * degree)
    a4 = mod(a10 + 180 * degree)

    l10 = RightAscension.reverse_get(a10)
    l7 = RightAscension.reverse_get(a7)
    l4 = RightAscension.reverse_get(a4)

    d0 = mod(l4 - ascendant) / 3
    d1 = mod(l7 - l4) / 3
    d2 = mod(l10 - l7) / 3
    d3 = mod(ascendant - l10) / 3

    return [
        mod(x)
        for x in [
            ascendant,
            ascendant + d0,
            ascendant + 2 * d0,
            l4,
            l4 + d1,
            l4 + 2 * d1,
            l7,
            l7 + d2,
            l7 + 2 * d2,
            l10,
            l10 + d3,
            l10 + 2 * d3,
        ]
    ]
