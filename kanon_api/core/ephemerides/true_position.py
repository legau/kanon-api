from typing import Type

from kanon.calendars import Date
from kanon.units.radices import BasedQuantity

from .tables import Moon, Sun, SuperiorPlanet
from .utils import mod


def sun_true_pos(date: Date) -> BasedQuantity:
    days = date.days_from_epoch()

    mean_sun_pos = Sun.mean_motion(days)

    mean_arg_sun = mean_sun_pos - Sun.get_apogee(days)

    eq_sun = Sun.equation(mod(mean_arg_sun.value))

    true_pos_sun = mod(mean_sun_pos - eq_sun)

    return true_pos_sun


def moon_true_pos(date: Date) -> BasedQuantity:
    days = date.days_from_epoch()

    mean_moon_pos = Moon.mean_motion(days)
    mean_sun_pos = Sun.mean_motion(days)
    mean_arg = Moon.mean_argument(days)

    moon_center = mod(mean_moon_pos - mean_sun_pos) * 2

    center_eq = Moon.equation_center(moon_center.value)

    min_prop = Moon.minuta_proportionalia(moon_center.value) >> 1

    true_arg = mean_arg + center_eq

    temp_eq_arg = Moon.equation_arg(true_arg.value)

    moon_diameter = Moon.diameter_diversion(true_arg.value) * min_prop.value

    equation_of_argument = abs(temp_eq_arg) + moon_diameter

    if true_arg.value < 180:
        equation_of_argument *= -1

    return mean_moon_pos + equation_of_argument


def outer_planet_true_pos(date: Date, planet: Type[SuperiorPlanet]) -> BasedQuantity:
    days = date.days_from_epoch()

    mean_pos = planet.mean_motion(days)
    sun_mean_pos = Sun.mean_motion(days)

    apogee = planet.get_apogee(days)

    mean_center = mod(mean_pos - apogee)

    mean_arg = mod(sun_mean_pos - mean_pos)

    center_equation = planet.center_equation(mean_center.value)

    true_center = center_equation + mean_center
    true_arg = mean_arg - center_equation

    min_prop = planet.min_prop(true_center.value) >> 1

    temp_eq_arg = planet.arg_equation(true_arg.value)

    diversity_func = planet.long_propior if min_prop > 0 else planet.long_longior

    diameter = diversity_func(true_arg.value) * min_prop.value

    equation_of_argument = abs(temp_eq_arg) + diameter

    if true_arg.value > 180:
        equation_of_argument *= -1

    return equation_of_argument + center_equation + mean_pos
