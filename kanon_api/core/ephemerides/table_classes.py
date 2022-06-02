import json
from pathlib import Path
from typing import Type, TypeVar, cast

from kanon.tables.htable import HTable
from kanon.tables.symmetries import Symmetry
from kanon.units import Sexagesimal
from kanon.units.radices import BasedQuantity, BasedReal
from kanon.utils.types.number_types import Real

from kanon_api.units import degree
from kanon_api.utils import DeferedMeta

from .utils import TableInput, make_mean_motion, mod, read_dishas, read_table_input

anti_mirror = Symmetry("mirror", sign=-1)
mirror = Symmetry("mirror")


class CelestialBody(metaclass=DeferedMeta):
    def __init__(self, tset: "TableSet", mean_motion: tuple[str, str] | None):
        self.tset = tset
        if mean_motion:
            self.mean_motion = make_mean_motion(mean_motion)


class FixedStars(CelestialBody):
    def __init__(
        self,
        tset: "TableSet",
        mean_motion: tuple[str, str],
        access_recess_mm: tuple[str, str],
        access_recess_eq: TableInput,
    ):
        super().__init__(tset, mean_motion)
        self.access_recess_mm = make_mean_motion(access_recess_mm)
        self.access_recess_eq = read_table_input(access_recess_eq)


class Moon(CelestialBody):
    def __init__(
        self,
        tset: "TableSet",
        mean_motion: tuple[str, str],
        mean_argument: tuple[str, str],
        equation_center: TableInput,
        equation_arg: TableInput,
        minuta_proportionalia: TableInput,
        diameter_diversion: TableInput,
    ):
        super().__init__(tset, mean_motion)
        self.mean_argument = make_mean_motion(mean_argument)
        self.equation_center = read_table_input(equation_center)
        self.equation_arg = read_table_input(equation_arg)
        self.minuta_proportionalia = read_table_input(minuta_proportionalia)
        self.diameter_diversion = read_table_input(diameter_diversion)


class Planet(CelestialBody):
    def __init__(
        self,
        tset: "TableSet",
        mean_motion: tuple[str, str] | None,
        apogee_radix: str | None,
    ):
        super().__init__(tset, mean_motion)
        if apogee_radix:
            self.apogee_radix = Sexagesimal(apogee_radix) * degree

    def get_apogee(self, days: float) -> BasedQuantity:
        mean_fixed_star_pos = self.tset.FixedStars.mean_motion(days)
        access_recess_pos = self.tset.FixedStars.access_recess_mm(days)

        eq_access_recess = self.tset.FixedStars.access_recess_eq(
            access_recess_pos.value
        )

        return mean_fixed_star_pos + eq_access_recess + self.apogee_radix


class Sun(Planet):
    def __init__(
        self,
        tset: "TableSet",
        mean_motion: tuple[str, str],
        apogee_radix: str,
        equation: TableInput,
    ):
        super().__init__(tset, mean_motion, apogee_radix)
        self.equation = read_table_input(equation)


class SuperiorPlanet(Planet):
    def __init__(
        self,
        tset: "TableSet",
        apogee_radix: str | None,
        center_equation: TableInput,
        arg_equation: TableInput,
        min_prop: TableInput,
        long_longior: TableInput,
        long_propior: TableInput,
        mean_motion: tuple[str, str] | None,
    ):
        super().__init__(tset, mean_motion, apogee_radix)
        self.center_equation = read_table_input(center_equation)
        self.arg_equation = read_table_input(arg_equation)
        self.min_prop = read_table_input(min_prop)
        self.long_longior = read_table_input(long_longior)
        self.long_propior = read_table_input(long_propior)


class Mars(SuperiorPlanet):
    ...


class Jupiter(SuperiorPlanet):
    ...


class Saturn(SuperiorPlanet):
    ...


class InferiorPlanet(SuperiorPlanet):
    def __init__(
        self,
        tset: "TableSet",
        center_equation: TableInput,
        arg_equation: TableInput,
        min_prop: TableInput,
        long_longior: TableInput,
        long_propior: TableInput,
        mean_argument: tuple[str, str],
        apogee_radix: str | None = None,
        mean_motion: tuple[str, str] | None = None,
    ):
        super().__init__(
            tset,
            apogee_radix,
            center_equation,
            arg_equation,
            min_prop,
            long_longior,
            long_propior,
            mean_motion,
        )
        self.mean_argument = make_mean_motion(mean_argument)

    def __getattr__(self, __name: str):
        return getattr(self.tset.Sun, __name)


class Venus(InferiorPlanet):
    ...


class Mercury(InferiorPlanet):
    ...


def reverse_table(tab: HTable) -> HTable:
    return tab.copy(set_index=tab.values_column)


class ObliqueAscension(metaclass=DeferedMeta):
    def __init__(self, tables: dict[float, int]):
        self.tables = {float(k): read_dishas(v) for k, v in tables.items()}

    def _find_index(self, latitude: float) -> tuple[float, float | None, float]:
        tab = self.tables

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

    def get(self, longitude: Real, latitude: float) -> BasedQuantity:

        tab = self.tables

        lower_idx, upper_idx, ratio = self._find_index(latitude)

        if upper_idx is None:
            return cast(BasedQuantity, tab[lower_idx].get(longitude))

        lower = cast(BasedQuantity, tab[lower_idx].get(longitude))
        upper = cast(BasedQuantity, tab[upper_idx].get(longitude))

        return lower + ratio * (upper - lower)

    def reverse_get(self, obl_ascension: Real, latitude: float) -> BasedQuantity:

        tab = self.tables

        lower_idx, upper_idx, ratio = self._find_index(latitude)

        if upper_idx is None:
            return cast(BasedQuantity, reverse_table(tab[lower_idx]).get(obl_ascension))

        lower_tab = tab[lower_idx]
        upper_tab = tab[upper_idx]

        interpolated_tab = lower_tab.copy()

        valcol = interpolated_tab.values_column

        interpolated_tab[valcol] += (upper_tab[valcol] - lower_tab[valcol]) * ratio

        return cast(BasedQuantity, reverse_table(interpolated_tab).get(obl_ascension))


class RightAscension(metaclass=DeferedMeta):
    def __init__(self, table: int) -> None:
        self.table = read_dishas(table)
        self.rtable = reverse_table(self.table)

    def get(self, longitude: BasedReal) -> BasedQuantity:  # pragma: no cover
        return mod(self.table.get(mod(longitude + 90)) - 90 * degree)

    def reverse_get(self, right_ascension: BasedReal) -> BasedQuantity:
        return mod(self.rtable.get(mod(right_ascension - 90)) + 90 * degree)


TableComp = CelestialBody | ObliqueAscension | RightAscension

T = TypeVar("T", bound=TableComp)


class TableSet:
    def __init__(self, file_name: str) -> None:
        with Path(__file__).parent.joinpath("table_sets", file_name).open(
            mode="r"
        ) as f:
            data = json.load(f)
        self.FixedStars = FixedStars(self, **data["FixedStars"])
        self.Sun = Sun(self, **data["Sun"])
        self.Moon = Moon(self, **data["Moon"])
        self.Mars = Mars(self, **data["Mars"])
        self.Venus = Venus(self, **data["Venus"])
        self.Mercury = Mercury(self, **data["Mercury"])
        self.Saturn = Saturn(self, **data["Saturn"])
        self.Jupiter = Jupiter(self, **data["Jupiter"])
        self.ObliqueAscension = ObliqueAscension(**data["ObliqueAscension"])
        self.RightAscension = RightAscension(**data["RightAscension"])

    def __call__(self, obj: Type[T]) -> T:
        return getattr(self, obj.__name__)
