from typing import cast

from astropy.units import degree
from astropy.units.core import Unit
from astropy.units.quantity import Quantity
from kanon.calendars import Date
from kanon.units import Sexagesimal

from kanon_api.ephemerides.utils import get_days, mean_motion, read_dishas

degree = cast(Unit, degree)

mm_mean_sun = mean_motion(193, Sexagesimal("4,38;21,0,30,28"))
mm_fixed_stars = mean_motion(236, Sexagesimal(0))
mm_access_recess = mean_motion(237, Sexagesimal("5,59;12,34"), zodiac_offset=2)

tab_eq_access_recess = read_dishas(238)
tab_eq_sun = read_dishas(19)


def sun_true_pos(date: Date) -> Quantity:
    sexa_date = get_days(date)

    mean_sun_pos = mm_mean_sun(sexa_date)
    mean_fixed_star_pos = mm_fixed_stars(sexa_date)
    access_recess_pos = mm_access_recess(sexa_date)

    eq_access_recess = tab_eq_access_recess.get(access_recess_pos.value)

    solar_apogee_pos = (
        mean_fixed_star_pos + eq_access_recess + Sexagesimal("1,11;25,23") * degree
    )

    mean_arg_sun = (
        mean_sun_pos
        + (Sexagesimal(6, 0) * degree if mean_sun_pos < solar_apogee_pos else 0)
        - solar_apogee_pos
    )

    eq_sun = tab_eq_sun.get(mean_arg_sun.value)

    true_pos_sun = (
        mean_sun_pos
        + (Sexagesimal(6, 0) * degree if mean_sun_pos < eq_sun else 0)
        - eq_sun
    )

    return true_pos_sun
