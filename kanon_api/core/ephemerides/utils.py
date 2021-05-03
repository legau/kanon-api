from typing import Callable, Protocol, TypeVar, cast

from kanon.tables.htable import HTable
from kanon.units.radices import BasedQuantity, BasedReal
from kanon.utils.types.number_types import Real

from ...units import degree

BasedType = TypeVar("BasedType", BasedReal, BasedQuantity)


def mod(value: BasedType, divisor: int = 360) -> BasedType:
    _value: BasedReal = value.value if isinstance(value, BasedQuantity) else value
    res = _value.__round__() % divisor
    res = res.resize(value.significant)
    if isinstance(value, BasedQuantity):
        return res * value.unit
    return res


def read_dishas(tab_id: int) -> HTable:
    return HTable.read(tab_id, format="dishas")


def position_from_table(
    ndays: float, tab: HTable, radix: BasedQuantity, width: int = 9
) -> BasedQuantity:
    coeff: BasedQuantity = cast(BasedQuantity, tab.get(2) / 2)
    coeff = coeff << 2 - width
    return mod(cast(BasedQuantity, coeff * ndays + radix))


class RealToBasedQuantity(Protocol):
    def __call__(self, _v: Real) -> BasedQuantity:
        ...


def basedstatic(func: Callable) -> RealToBasedQuantity:
    return cast(RealToBasedQuantity, staticmethod(func))


def mean_motion(tab_id: int, radix: BasedQuantity, **kwargs) -> RealToBasedQuantity:
    def func(days: float) -> BasedQuantity:
        table = read_dishas(tab_id)
        return position_from_table(days, table, radix * degree, **kwargs)

    return basedstatic(func)
