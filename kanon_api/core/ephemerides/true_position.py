from kanon.calendars import Date
from kanon.units import Sexagesimal
from kanon.units.radices import BasedQuantity

from ...units import degree
from .tables import FIXED_STARS, MOON, SUN
from .utils import mod

SUN_APOGEE: BasedQuantity = Sexagesimal("1,11;25,23") * degree


def sun_true_pos(date: Date) -> BasedQuantity:
    days = date.days_from_epoch()

    mean_sun_pos = SUN.mean_motion(days)
    mean_fixed_star_pos = FIXED_STARS.mean_motion(days)
    access_recess_pos = FIXED_STARS.access_recess_mm(days)

    eq_access_recess = FIXED_STARS.access_recess_eq(access_recess_pos.value)

    solar_apogee_pos = mean_fixed_star_pos + eq_access_recess + SUN_APOGEE

    mean_arg_sun = mean_sun_pos - solar_apogee_pos

    eq_sun = SUN.equation(mod(mean_arg_sun.value))

    true_pos_sun = mod(mean_sun_pos - eq_sun)

    return true_pos_sun


def moon_true_pos(date: Date) -> BasedQuantity:
    days = date.days_from_epoch()

    mean_moon_pos = MOON.mean_motion(days)
    mean_sun_pos = SUN.mean_motion(days)
    mean_arg = MOON.mean_argument(days)

    moon_center = mod(mean_moon_pos - mean_sun_pos) * 2

    center_eq = MOON.equation_center(moon_center.value)

    min_prop = MOON.minuta_proportionalia(moon_center.value) >> 1

    true_arg = mean_arg + center_eq

    temp_eq_arg = MOON.equation_arg(true_arg.value)

    moon_diameter = MOON.diameter_diversion(true_arg.value) * min_prop.value

    equation_of_argument = abs(temp_eq_arg) + moon_diameter

    if true_arg.value < 180:
        equation_of_argument *= -1

    return mean_moon_pos + equation_of_argument
