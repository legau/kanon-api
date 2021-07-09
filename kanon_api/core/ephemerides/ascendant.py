from kanon.units.radices import BasedQuantity

from .tables import ObliqueAscension
from .true_position import sun_true_pos
from .utils import mod


def ascendant(days: float, latitude: float) -> BasedQuantity:
    sun = sun_true_pos(days)

    sun_rising = ObliqueAscension.get(sun, latitude)
    sun_setting = ObliqueAscension.get(mod(sun.value + 180), latitude)

    diurnal_arc = mod(sun_setting - sun_rising)

    ascension_degree = mod(sun_rising + diurnal_arc / 2)

    return ObliqueAscension.reverse_get(ascension_degree, latitude)
