from typing import Type

from kanon.calendars import Date
from kanon.units.radices import BasedQuantity

from .tables import MOON, SUN, OuterPlanet
from .utils import mod


def sun_true_pos(date: Date) -> BasedQuantity:
    days = date.days_from_epoch()

    mean_sun_pos = SUN.mean_motion(days)

    mean_arg_sun = mean_sun_pos - SUN.get_apogee(days)

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


def outer_planet_true_pos(date: Date, planet: Type[OuterPlanet]) -> BasedQuantity:
    raise NotImplementedError
