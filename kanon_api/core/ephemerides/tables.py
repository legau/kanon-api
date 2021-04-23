from enum import Enum

from kanon.tables.symmetries import Symmetry
from kanon.units import Sexagesimal
from kanon.units.radices import BasedQuantity

from .utils import mean_motion, read_dishas


class PlanetEnum(Enum):
    def __call__(self, *args, **kwds) -> BasedQuantity:
        ...


anti_mirror = Symmetry("mirror", sign=-1)
mirror = Symmetry("mirror")

_sun_eq_table = read_dishas(19)
_sun_eq_table.symmetry.append(mirror)


class SUN(PlanetEnum):
    mean_motion = mean_motion(193, Sexagesimal("4,38;21,0,30,28"))
    equation = _sun_eq_table.get


_moon_arg_eq_table = read_dishas(182)
_moon_arg_eq_table.symmetry.append(anti_mirror)
_moon_center_eq_table = read_dishas(181)
_moon_center_eq_table.symmetry.append(anti_mirror)
_moon_minuta_prop = read_dishas(239)
_moon_minuta_prop.symmetry.append(mirror)


class MOON(PlanetEnum):
    mean_argument = mean_motion(197, Sexagesimal(0))
    mean_motion = mean_motion(194, Sexagesimal("2,2;46,50,16,39"))
    equation_center = _moon_center_eq_table.get
    equation_arg = _moon_arg_eq_table.get
    minuta_proportionalia = _moon_minuta_prop.get


_fs_access_recess_eq_table = read_dishas(238)
_fs_access_recess_eq_table.symmetry = [
    mirror,
    Symmetry("periodic", targets=[Sexagesimal(3, 1)]),
]


class FIXED_STARS(PlanetEnum):
    access_recess_mm = mean_motion(237, Sexagesimal("5,59;12,34"), zodiac_offset=2)
    mean_motion = mean_motion(236, Sexagesimal(0))
    access_recess_eq = _fs_access_recess_eq_table.get
