from typing import cast

from kanon.calendars.calendars import Date
from kanon.units.radices import BasedQuantity

from .true_position import sun_true_pos
from .utils import mod, read_dishas


def ascendant(date: Date):
    sun = sun_true_pos(date)

    oblique_ascension = read_dishas(257)

    sun_rising = cast(BasedQuantity, oblique_ascension.get(sun.value))
    sun_setting = cast(BasedQuantity, oblique_ascension.get(mod(sun.value + 180)))

    diurnal_arc = mod(sun_setting - sun_rising)

    ascension_degree = mod(sun_rising + diurnal_arc / 2)

    return oblique_ascension.copy(set_index=oblique_ascension.values_column).get(
        ascension_degree.value
    )
