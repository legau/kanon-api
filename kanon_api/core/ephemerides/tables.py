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
_sun_eq_table.symmetry.append(anti_mirror)


class SUN(PlanetEnum):
    mean_motion = mean_motion(193, Sexagesimal("4,38;21,0,30,28"))
    equation = _sun_eq_table.get


class MOON(PlanetEnum):
    mean_argument = mean_motion(195, Sexagesimal("3,19;0,14,31,16"))
    mean_motion = mean_motion(194, Sexagesimal("2,2;46,50,16,39"))
    equation_center = read_dishas(181).get
    equation_arg = read_dishas(182).get
    minuta_proportionalia = read_dishas(239).get
    diameter_diversion = read_dishas(240).get


_fs_access_recess_eq_table = read_dishas(238)
_fs_access_recess_eq_table.symmetry = [
    mirror,
    Symmetry("periodic", targets=[Sexagesimal(3, 1)]),
]


class FIXED_STARS(PlanetEnum):
    access_recess_mm = mean_motion(237, Sexagesimal("5,59;12,34"), width=7)
    mean_motion = mean_motion(236, Sexagesimal(0))
    access_recess_eq = _fs_access_recess_eq_table.get
