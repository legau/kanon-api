from typing import cast

from kanon.units.radices import BasedQuantity

from .tables import oblique_ascension, reverse_obl_ascension
from .true_position import sun_true_pos
from .utils import mod


def ascendant(days: float):
    sun = sun_true_pos(days)

    sun_rising = cast(BasedQuantity, oblique_ascension.get(sun.value))
    sun_setting = cast(BasedQuantity, oblique_ascension.get(mod(sun.value + 180)))

    diurnal_arc = mod(sun_setting - sun_rising)

    ascension_degree = mod(sun_rising + diurnal_arc / 2)

    return reverse_obl_ascension.get(ascension_degree.value)
