from abc import ABCMeta, abstractmethod

from kanon.tables.symmetries import Symmetry
from kanon.units import Sexagesimal
from kanon.units.radices import BasedQuantity
from kanon.utils.types.number_types import Real

from ...units import degree
from .utils import basedstatic, mean_motion, read_dishas, read_from_table

anti_mirror = Symmetry("mirror", sign=-1)
mirror = Symmetry("mirror")


class CelestialBody(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def mean_motion(_v: float) -> BasedQuantity:
        raise NotImplementedError


_fs_access_recess_eq_table = read_dishas(238)
_fs_access_recess_eq_table.symmetry = [
    mirror,
    Symmetry("periodic", targets=[Sexagesimal(3, 1)]),
]


class FixedStars(CelestialBody):
    access_recess_mm = mean_motion(
        Sexagesimal("0 ; 00,00,30,24,49"), Sexagesimal("5,59;12,34")
    )
    mean_motion = mean_motion(Sexagesimal("0 ; 00,00,04,20,41,17,12"), Sexagesimal(0))
    access_recess_eq = basedstatic(_fs_access_recess_eq_table.get)


class Moon(CelestialBody):
    mean_argument = mean_motion(
        Sexagesimal("13 ; 03,53,57,30,21,04,13"), Sexagesimal("3,19;0,14,31,16")
    )
    mean_motion = mean_motion(
        Sexagesimal("13 ; 10,35,01,15,11,04,35"), Sexagesimal("2,2;46,50,16,39")
    )
    equation_center = read_from_table(181)
    equation_arg = read_from_table(182)
    minuta_proportionalia = read_from_table(239)
    diameter_diversion = read_from_table(240)


class Planet(CelestialBody):
    apogee_radix: BasedQuantity

    @classmethod
    def get_apogee(cls, days: float) -> BasedQuantity:
        mean_fixed_star_pos = FixedStars.mean_motion(days)
        access_recess_pos = FixedStars.access_recess_mm(days)

        eq_access_recess = FixedStars.access_recess_eq(access_recess_pos.value)

        return mean_fixed_star_pos + eq_access_recess + cls.apogee_radix


_sun_eq_table = read_dishas(19)
_sun_eq_table.symmetry.append(anti_mirror)


class Sun(Planet):
    equation = basedstatic(_sun_eq_table.get)
    mean_motion = mean_motion(
        Sexagesimal("00;59,08,19,37,19,13,56"), Sexagesimal("4,38;21,0,30,28")
    )
    apogee_radix = Sexagesimal("1,11;25,23") * degree


class SuperiorPlanet(Planet):
    @staticmethod
    @abstractmethod
    def center_equation(_v: Real) -> BasedQuantity:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def arg_equation(_v: Real) -> BasedQuantity:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def min_prop(_v: Real) -> BasedQuantity:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def long_longior(_v: Real) -> BasedQuantity:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def long_propior(_v: Real) -> BasedQuantity:
        raise NotImplementedError


class Mars(SuperiorPlanet):
    apogee_radix = Sexagesimal("1,55;12,13,4") * degree
    mean_motion = mean_motion(
        Sexagesimal("0 ; 31,26,38,40,05"), Sexagesimal("0,41;25,29,43")
    )
    center_equation = read_from_table(187)
    arg_equation = read_from_table(188)
    min_prop = read_from_table(249)
    long_longior = read_from_table(247)
    long_propior = read_from_table(248)


class Jupiter(SuperiorPlanet):
    apogee_radix = Sexagesimal("2,33;37,0,4") * degree
    mean_motion = mean_motion(
        Sexagesimal("0 ; 04,59,15,27,07,23,50"), Sexagesimal("3,0;37,20,43")
    )
    center_equation = read_from_table(185)
    arg_equation = read_from_table(186)
    min_prop = read_from_table(246)
    long_longior = read_from_table(244)
    long_propior = read_from_table(245)


class Saturn(SuperiorPlanet):
    apogee_radix = Sexagesimal("3,53;23,42,4") * degree
    mean_motion = mean_motion(
        Sexagesimal("0 ; 02,00,35,17,40,21"), Sexagesimal("1,14;5,20,12")
    )
    center_equation = read_from_table(235)
    arg_equation = read_from_table(184)
    min_prop = read_from_table(243)
    long_longior = read_from_table(241)
    long_propior = read_from_table(242)


class InferiorPlanet(SuperiorPlanet, Sun):
    @staticmethod
    @abstractmethod
    def mean_argument(_v: Real) -> BasedQuantity:
        raise NotImplementedError

    @staticmethod
    def equation(_v: Real) -> BasedQuantity:
        raise NotImplementedError


class Venus(InferiorPlanet):
    mean_argument = mean_motion(
        Sexagesimal("0 ; 36,59,27,23,59,31"), Sexagesimal("2,9;22,2,36")
    )
    center_equation = read_from_table(189)
    arg_equation = read_from_table(190)
    min_prop = read_from_table(252)
    long_longior = read_from_table(250)
    long_propior = read_from_table(251)


class Mercury(InferiorPlanet):
    apogee_radix = Sexagesimal("3,10;39,33,4") * degree
    mean_argument = mean_motion(
        Sexagesimal("03 ; 06,24,07,42,40,52"), Sexagesimal("45;23,58,0")
    )
    center_equation = read_from_table(191)
    arg_equation = read_from_table(192)
    min_prop = read_from_table(255)
    long_longior = read_from_table(253)
    long_propior = read_from_table(254)


Sun(), Moon(), Mercury(), Venus(), Mars(), Jupiter(), Saturn(), FixedStars()
