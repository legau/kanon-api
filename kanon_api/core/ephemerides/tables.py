from typing import Callable

from kanon.tables.symmetries import Symmetry
from kanon.units import Sexagesimal
from kanon.units.precision import FuncEnum
from kanon.units.radices import BasedQuantity, BasedReal

from .utils import mean_motion, read_dishas

TableSolver = Callable[[BasedReal], BasedQuantity]


class PlanetEnum(FuncEnum):
    mean_motion: TableSolver
    equation: TableSolver
    access_recess_mm: TableSolver
    access_recess_eq: TableSolver


_sun_eq_table = read_dishas(19)
_sun_eq_table.symmetry.append(Symmetry("mirror", sign=-1))


class SUN(PlanetEnum):
    mean_motion = mean_motion(193, Sexagesimal("4,38;21,0,30,28"))
    equation = _sun_eq_table.get


_fs_access_recess_eq_table = read_dishas(238)
_fs_access_recess_eq_table.symmetry = [
    Symmetry("mirror"),
    Symmetry("periodic", targets=[Sexagesimal(3, 1)]),
]


class FIXED_STARS(PlanetEnum):
    access_recess_mm = mean_motion(237, Sexagesimal("5,59;12,34"), zodiac_offset=2)
    mean_motion = mean_motion(236, Sexagesimal(0))
    access_recess_eq = _fs_access_recess_eq_table.get
