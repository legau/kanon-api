from typing import Callable, Literal, Protocol, TypeVar, cast, runtime_checkable

from kanon.tables.htable import HTable
from kanon.tables.symmetries import Symmetry
from kanon.units import Sexagesimal
from kanon.units.radices import BasedQuantity, BasedReal
from kanon.utils.types.number_types import Real

from kanon_api.units import degree

BasedType = TypeVar("BasedType", BasedReal, BasedQuantity)


def mod(value: BasedType, divisor: int = 360) -> BasedType:
    return value % (divisor * (value.unit if isinstance(value, BasedQuantity) else 1))


def read_dishas(tab_id: int) -> HTable:
    table: HTable = HTable.read(tab_id)
    table[table.values_column] = table[table.values_column].astype(Sexagesimal)
    table.freeze()
    return table


@runtime_checkable
class RealToBasedQuantity(Protocol):
    def __call__(self, _v: Real) -> BasedQuantity:
        ...


def basedstatic(func: Callable) -> RealToBasedQuantity:
    return cast(RealToBasedQuantity, staticmethod(func))


def read_from_table(
    tab_id: int, symmetry: list[Symmetry] | None = None
) -> RealToBasedQuantity:

    table = read_dishas(tab_id)
    if symmetry:
        table.symmetry = symmetry
    table.freeze()
    return basedstatic(table.get)


def build_symmetry(
    sym: Literal["mirror", "periodic", "anti_mirror"] | dict
) -> Symmetry:
    if sym == "anti_mirror":
        return Symmetry("mirror", sign=-1)
    if isinstance(sym, dict):
        return Symmetry(
            sym["type"], targets=[Sexagesimal(target) for target in sym["targets"]]
        )
    return Symmetry(sym)


TableInput = int | dict


def read_table_input(table_input: TableInput):
    table_id = table_input if isinstance(table_input, int) else table_input["id"]
    symmetries = None
    if isinstance(table_input, dict):
        symmetries = [build_symmetry(sym) for sym in table_input.get("symmetries", [])]
    return read_from_table(table_id, symmetries)


def make_mean_motion(raw_input: tuple[str, str]):

    mm = (Sexagesimal(raw_input[0]), Sexagesimal(raw_input[1]))

    def func(days: float) -> BasedQuantity:
        return mod(mm[0] * days + mm[1]) * degree

    return staticmethod(func)
