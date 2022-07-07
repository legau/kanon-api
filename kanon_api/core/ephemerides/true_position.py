from kanon.units.radices import BasedQuantity

from .table_classes import InferiorPlanet, SuperiorPlanet, TableSet
from .utils import mod


def sun_true_pos(table_set: TableSet, days: float) -> BasedQuantity:
    mean_sun_pos = table_set.Sun.mean_motion(days)

    mean_arg_sun = mean_sun_pos - table_set.Sun.get_apogee(days)

    eq_sun = table_set.Sun.equation(mod(mean_arg_sun))

    true_pos_sun = mod(mean_sun_pos - eq_sun)

    return true_pos_sun


def moon_true_pos(table_set: TableSet, days: float) -> BasedQuantity:
    mean_moon_pos = table_set.Moon.mean_motion(days)
    mean_sun_pos = table_set.Sun.mean_motion(days)
    mean_arg = table_set.Moon.mean_argument(days)

    moon_center = mod((mean_moon_pos - mean_sun_pos) * 2)

    center_eq = table_set.Moon.equation_center(moon_center)

    min_prop = table_set.Moon.minuta_proportionalia(moon_center) >> 1

    true_arg = mean_arg + center_eq

    temp_eq_arg = table_set.Moon.equation_arg(true_arg)

    moon_diameter = table_set.Moon.diameter_diversion(true_arg) * min_prop.value

    equation_of_argument = abs(temp_eq_arg) + moon_diameter

    if true_arg.value < 180:
        equation_of_argument *= -1

    return mod(mean_moon_pos + equation_of_argument)


def planet_true_pos(days: float, planet: SuperiorPlanet) -> BasedQuantity:
    mean_pos = planet.mean_motion(days)

    apogee = planet.get_apogee(days)

    mean_center = mod(mean_pos - apogee)

    mean_arg: BasedQuantity
    if isinstance(planet, InferiorPlanet):
        mean_arg = planet.mean_argument(days)
    else:
        sun_mean_pos = planet.tset.Sun.mean_motion(days)
        mean_arg = mod(sun_mean_pos - mean_pos)

    center_equation = planet.center_equation(mean_center)

    true_center = center_equation + mean_center
    true_arg = mean_arg - center_equation

    min_prop = planet.min_prop(true_center) >> 1

    temp_eq_arg = planet.arg_equation(true_arg)

    diversity_func = planet.long_propior if min_prop > 0 else planet.long_longior

    diameter = diversity_func(true_arg) * min_prop.value

    equation_of_argument = abs(temp_eq_arg) + diameter

    if true_arg.value > 180:
        equation_of_argument *= -1

    return mod(equation_of_argument + center_equation + mean_pos)
