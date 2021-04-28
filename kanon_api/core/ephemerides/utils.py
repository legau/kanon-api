from typing import Callable, TypeVar, cast

from kanon.calendars import Date
from kanon.tables.htable import HTable
from kanon.units import Sexagesimal
from kanon.units.radices import BasedQuantity, BasedReal

from ...units import degree

BasedType = TypeVar("BasedType", BasedReal, BasedQuantity)


def mod(value: BasedType, divisor: int = 360) -> BasedType:
    _value: BasedReal = value.value if isinstance(value, BasedQuantity) else value
    res = _value % divisor
    res = res.resize(value.significant)
    if isinstance(value, BasedQuantity):
        return res * value.unit
    return res


def read_dishas(tab_id: int) -> HTable:
    return HTable.read(tab_id, format="dishas")


def position_from_table(
    ndays: float, tab: HTable, radix: BasedQuantity, width: int = 9
) -> BasedQuantity:
    coeff: BasedQuantity = cast(BasedQuantity, tab.get(1))
    coeff = coeff << 2 - width
    return mod(cast(BasedQuantity, coeff * ndays + radix))


def mean_motion(
    tab_id: int, radix: BasedQuantity, **kwargs
) -> Callable[[float], BasedQuantity]:
    def func(days: float) -> BasedQuantity:
        table = read_dishas(tab_id)
        return position_from_table(days, table, radix * degree, **kwargs)

    return func


def get_days(date: Date) -> BasedReal:
    return Sexagesimal.from_float(date.days_from_epoch(), 0)
