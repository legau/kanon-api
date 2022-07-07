from kanon.units.radices import BasedQuantity

from kanon_api.core.ephemerides.table_classes import TableSet

from .true_position import sun_true_pos
from .utils import mod


def ascendant(table_set: TableSet, days: float, latitude: float) -> BasedQuantity:
    sun = sun_true_pos(table_set, round(days)).value

    hours_arc = (days - round(days)) * 24 * 15

    sun_rising = table_set.ObliqueAscension.get(sun, latitude).value
    sun_setting = table_set.ObliqueAscension.get(mod(sun + 180), latitude).value

    diurnal_arc = mod(sun_setting - sun_rising)

    ascension_degree = mod(sun_rising + hours_arc + diurnal_arc / 2)

    return table_set.ObliqueAscension.reverse_get(ascension_degree, latitude)
