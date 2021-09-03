from typing import Callable, Protocol, TypeVar, cast

from kanon.tables.htable import HTable
from kanon.units.radices import BasedQuantity, BasedReal
from kanon.utils.types.number_types import Real

from kanon_api.units import degree

BasedType = TypeVar("BasedType", BasedReal, BasedQuantity)


def mod(value: BasedType, divisor: int = 360) -> BasedType:
    return value % (divisor * (value.unit if isinstance(value, BasedQuantity) else 1))


def read_dishas(tab_id: int) -> HTable:
    return HTable.read(tab_id)


class RealToBasedQuantity(Protocol):
    def __call__(self, _v: Real) -> BasedQuantity:
        ...


def basedstatic(func: Callable) -> RealToBasedQuantity:
    return cast(RealToBasedQuantity, staticmethod(func))


def read_from_table(_id: int) -> RealToBasedQuantity:
    return basedstatic(read_dishas(_id).get)


def mean_motion(parameter: BasedReal, radix: BasedReal) -> RealToBasedQuantity:
    def func(days: float) -> BasedQuantity:
        return mod(parameter * days + radix) * degree

    return basedstatic(func)
