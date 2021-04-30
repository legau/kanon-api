from abc import ABCMeta, abstractmethod

from kanon.tables.symmetries import Symmetry
from kanon.units import Sexagesimal
from kanon.units.radices import BasedQuantity

from ...units import degree
from .utils import basedstatic, mean_motion, read_dishas

anti_mirror = Symmetry("mirror", sign=-1)
mirror = Symmetry("mirror")


_fs_access_recess_eq_table = read_dishas(238)
_fs_access_recess_eq_table.symmetry = [
    mirror,
    Symmetry("periodic", targets=[Sexagesimal(3, 1)]),
]


class FIXED_STARS:
    access_recess_mm = mean_motion(237, Sexagesimal("5,59;12,34"), width=7)
    mean_motion = mean_motion(236, Sexagesimal(0))
    access_recess_eq = basedstatic(_fs_access_recess_eq_table.get)


class Planet(metaclass=ABCMeta):
    apogee_radix: BasedQuantity

    @staticmethod
    @abstractmethod
    def mean_motion(days: float) -> BasedQuantity:
        raise NotImplementedError

    @classmethod
    def get_apogee(cls, days: float) -> BasedQuantity:
        mean_fixed_star_pos = FIXED_STARS.mean_motion(days)
        access_recess_pos = FIXED_STARS.access_recess_mm(days)

        eq_access_recess = FIXED_STARS.access_recess_eq(access_recess_pos.value)

        return mean_fixed_star_pos + eq_access_recess + cls.apogee_radix


class OuterPlanet(Planet):
    pass


class InnerPlanet(Planet):
    pass


_sun_eq_table = read_dishas(19)
_sun_eq_table.symmetry.append(anti_mirror)


class SUN(Planet):
    mean_motion = mean_motion(193, Sexagesimal("4,38;21,0,30,28"))
    equation = basedstatic(_sun_eq_table.get)
    apogee_radix = Sexagesimal("1,11;25,23") * degree


class MOON(Planet):
    mean_argument = mean_motion(195, Sexagesimal("3,19;0,14,31,16"))
    mean_motion = mean_motion(194, Sexagesimal("2,2;46,50,16,39"))
    equation_center = basedstatic(read_dishas(181).get)
    equation_arg = basedstatic(read_dishas(182).get)
    minuta_proportionalia = basedstatic(read_dishas(239).get)
    diameter_diversion = basedstatic(read_dishas(240).get)


class VENUS(InnerPlanet):
    apogee_radix = Sexagesimal("1,11;25,23") * degree


class MERCURY(InnerPlanet):
    apogee_radix = Sexagesimal("3,10;39,33,4") * degree


class MARS(OuterPlanet):
    apogee_radix = Sexagesimal("1,55;12,13,4") * degree


class JUPITER(OuterPlanet):
    apogee_radix = Sexagesimal("2,33;37,0,4") * degree


class SATURN(OuterPlanet):
    apogee_radix = Sexagesimal("3,53;23,42,4") * degree
