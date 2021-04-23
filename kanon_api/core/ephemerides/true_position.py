from kanon.calendars import Date
from kanon.units import Sexagesimal
from kanon.units.radices import BasedQuantity

from ...units import degree
from .tables import FIXED_STARS, MOON, SUN
from .utils import get_days, mod360

SUN_APOGEE: BasedQuantity = Sexagesimal("1,11;25,23") * degree


def sun_true_pos(date: Date) -> BasedQuantity:
    sexa_date = get_days(date)

    mean_sun_pos = SUN.mean_motion(sexa_date)
    mean_fixed_star_pos = FIXED_STARS.mean_motion(sexa_date)
    access_recess_pos = FIXED_STARS.access_recess_mm(sexa_date)

    eq_access_recess = FIXED_STARS.access_recess_eq(access_recess_pos.value)

    solar_apogee_pos = mean_fixed_star_pos + eq_access_recess + SUN_APOGEE

    mean_arg_sun = mod360(mean_sun_pos - solar_apogee_pos)

    eq_sun = SUN.equation(mean_arg_sun.value)

    true_pos_sun = mod360(mean_sun_pos - eq_sun)

    return true_pos_sun


def moon_true_pos(date: Date) -> BasedQuantity:
    sexa_date = get_days(date)

    mean_moon_pos = MOON.mean_motion(sexa_date)
    mean_sun_pos = SUN.mean_motion(sexa_date)
    mean_arg = MOON.mean_argument(sexa_date)

    moon_center = (mean_moon_pos - mean_sun_pos) * 2

    center_eq = MOON.equation_center(moon_center)

    min_prop = MOON.minuta_proportionalia(moon_center)

    true_arg = mean_arg + (center_eq * 1 if moon_center < 180 else -1)

    arg_eq = MOON.equation_arg(true_arg)

    min_prop, arg_eq
