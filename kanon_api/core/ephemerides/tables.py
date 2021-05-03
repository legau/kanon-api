from abc import ABCMeta, abstractmethod

from kanon.tables.symmetries import Symmetry
from kanon.units import Sexagesimal
from kanon.units.radices import BasedQuantity
from kanon.utils.types.number_types import Real

from ...units import degree
from .utils import basedstatic, mean_motion, read_dishas

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
    access_recess_mm = mean_motion(237, Sexagesimal("5,59;12,34"), width=7)
    mean_motion = mean_motion(236, Sexagesimal(0))
    access_recess_eq = basedstatic(_fs_access_recess_eq_table.get)


class Moon(CelestialBody):
    mean_argument = mean_motion(195, Sexagesimal("3,19;0,14,31,16"))
    mean_motion = mean_motion(194, Sexagesimal("2,2;46,50,16,39"))
    equation_center = basedstatic(read_dishas(181).get)
    equation_arg = basedstatic(read_dishas(182).get)
    minuta_proportionalia = basedstatic(read_dishas(239).get)
    diameter_diversion = basedstatic(read_dishas(240).get)


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
    mean_motion = mean_motion(193, Sexagesimal("4,38;21,0,30,28"))
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
    mean_motion = mean_motion(208, Sexagesimal("0,41;25,29,43"), width=7)
    center_equation = basedstatic(read_dishas(187).get)
    arg_equation = basedstatic(read_dishas(188).get)
    min_prop = basedstatic(read_dishas(249).get)
    long_longior = basedstatic(read_dishas(247).get)
    long_propior = basedstatic(read_dishas(248).get)


class Jupiter(SuperiorPlanet):
    apogee_radix = Sexagesimal("2,33;37,0,4") * degree
    mean_motion = mean_motion(207, Sexagesimal("3,0;37,20,43"))
    center_equation = basedstatic(read_dishas(185).get)
    arg_equation = basedstatic(read_dishas(186).get)
    min_prop = basedstatic(read_dishas(246).get)
    long_longior = basedstatic(read_dishas(244).get)
    long_propior = basedstatic(read_dishas(245).get)


class Saturn(SuperiorPlanet):
    apogee_radix = Sexagesimal("3,53;23,42,4") * degree
    mean_motion = mean_motion(206, Sexagesimal("1,14;5,20,12"), width=8)
    center_equation = basedstatic(read_dishas(235).get)
    arg_equation = basedstatic(read_dishas(184).get)
    min_prop = basedstatic(read_dishas(243).get)
    long_longior = basedstatic(read_dishas(241).get)
    long_propior = basedstatic(read_dishas(242).get)


class InferiorPlanet(SuperiorPlanet, Sun):
    @staticmethod
    @abstractmethod
    def mean_argument(_v: Real) -> BasedQuantity:
        raise NotImplementedError

    @staticmethod
    def equation(_v: Real) -> BasedQuantity:
        raise NotImplementedError


class Venus(InferiorPlanet):
    mean_argument = mean_motion(209, Sexagesimal("2,9;22,2,36"), width=8)
    center_equation = basedstatic(read_dishas(189).get)
    arg_equation = basedstatic(read_dishas(190).get)
    min_prop = basedstatic(read_dishas(252).get)
    long_longior = basedstatic(read_dishas(250).get)
    long_propior = basedstatic(read_dishas(251).get)


class Mercury(InferiorPlanet):
    apogee_radix = Sexagesimal("3,10;39,33,4") * degree
    mean_argument = mean_motion(210, Sexagesimal("45;23,58,0"), width=8)
    center_equation = basedstatic(read_dishas(191).get)
    arg_equation = basedstatic(read_dishas(192).get)
    min_prop = basedstatic(read_dishas(255).get)
    long_longior = basedstatic(read_dishas(253).get)
    long_propior = basedstatic(read_dishas(254).get)


Sun(), Moon(), Mercury(), Venus(), Mars(), Jupiter(), Saturn(), FixedStars()
