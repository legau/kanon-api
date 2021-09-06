from typing import Union, cast

from kanon.tables.htable import HTable
from kanon.tables.symmetries import Symmetry
from kanon.units import Sexagesimal
from kanon.units.radices import BasedQuantity
from kanon.utils.types.number_types import Real

from kanon_api.units import degree
from kanon_api.utils import StaticMeta

from .utils import mean_motion, read_dishas, read_from_table

anti_mirror = Symmetry("mirror", sign=-1)
mirror = Symmetry("mirror")


class CelestialBody(metaclass=StaticMeta):
    @staticmethod
    def mean_motion(_v: float) -> BasedQuantity:
        raise NotImplementedError


class FixedStars(CelestialBody):
    access_recess_mm = mean_motion(
        Sexagesimal("0 ; 00,00,30,24,49"), Sexagesimal("5,59;12,34")
    )
    mean_motion = mean_motion(Sexagesimal("0 ; 00,00,04,20,41,17,12"), Sexagesimal(0))
    access_recess_eq = read_from_table(
        238,
        symmetry=[
            mirror,
            Symmetry("periodic", targets=[Sexagesimal(3, 1)]),
        ],
    )


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


class Sun(Planet):
    equation = read_from_table(19, symmetry=[anti_mirror])
    mean_motion = mean_motion(
        Sexagesimal("00;59,08,19,37,19,13,56"), Sexagesimal("4,38;21,0,30,28")
    )
    apogee_radix = Sexagesimal("1,11;25,23") * degree


class SuperiorPlanet(Planet):
    @staticmethod
    def center_equation(_v: Real) -> BasedQuantity:
        raise NotImplementedError

    @staticmethod
    def arg_equation(_v: Real) -> BasedQuantity:
        raise NotImplementedError

    @staticmethod
    def min_prop(_v: Real) -> BasedQuantity:
        raise NotImplementedError

    @staticmethod
    def long_longior(_v: Real) -> BasedQuantity:
        raise NotImplementedError

    @staticmethod
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


def reverse_table(tab: HTable) -> HTable:
    return tab.copy(set_index=tab.values_column)


class ObliqueAscension(metaclass=StaticMeta):
    tables: dict[float, HTable] = {
        16: read_dishas(300),
        24: read_dishas(301),
        30: read_dishas(302),
        36: read_dishas(303),
        41.5: read_dishas(304),
        45: read_dishas(305),
        48: read_dishas(306),
    }

    @classmethod
    def _find_index(cls, latitude: float) -> tuple[float, Union[float, None], float]:
        tab = cls.tables

        if (
            (idx := latitude) in tab
            or latitude < (idx := min(tab))
            or latitude > (idx := max(tab))
        ):
            return idx, None, 0

        arr = [x - latitude for x in tab]

        lower_idx = max(x for x in arr if x < 0) + latitude
        upper_idx = min(x for x in arr if x > 0) + latitude
        ratio = (latitude - lower_idx) / (upper_idx - lower_idx)

        return lower_idx, upper_idx, ratio

    @classmethod
    def get(cls, longitude: Real, latitude: float) -> BasedQuantity:

        tab = cls.tables

        lower_idx, upper_idx, ratio = cls._find_index(latitude)

        if upper_idx is None:
            return cast(BasedQuantity, tab[lower_idx].get(longitude))

        lower = cast(BasedQuantity, tab[lower_idx].get(longitude))
        upper = cast(BasedQuantity, tab[upper_idx].get(longitude))

        return lower + ratio * (upper - lower)

    @classmethod
    def reverse_get(cls, obl_ascension: Real, latitude: float) -> BasedQuantity:

        tab = cls.tables

        lower_idx, upper_idx, ratio = cls._find_index(latitude)

        if upper_idx is None:
            return cast(BasedQuantity, reverse_table(tab[lower_idx]).get(obl_ascension))

        lower_tab = tab[lower_idx]
        upper_tab = tab[upper_idx]

        interpolated_tab = lower_tab.copy()

        valcol = interpolated_tab.values_column

        interpolated_tab[valcol] += (upper_tab[valcol] - lower_tab[valcol]) * ratio

        return cast(BasedQuantity, reverse_table(interpolated_tab).get(obl_ascension))
