from typing import Callable

import astropy.units as u
from kanon.calendars import Date
from kanon.tables.htable import HTable
from kanon.units import Sexagesimal
from kanon.units.radices import BasedQuantity


def read_dishas(tab_id: int) -> HTable:
    return HTable.read(tab_id, format="dishas")


def position_from_table(
    ndays: Sexagesimal,
    tab: HTable,
    radix: BasedQuantity,
    zodiac_offset: int = 4,
) -> BasedQuantity:

    result = radix
    for i, v in enumerate(ndays[:]):
        result += tab.get(v) >> (i + 4 - len(ndays[:])) + zodiac_offset
    result %= Sexagesimal(6, 0) * u.degree
    return result


def mean_motion(
    tab_id: int, radix: Sexagesimal, **kwargs
) -> Callable[[Sexagesimal], BasedQuantity]:
    def func(days: Sexagesimal) -> BasedQuantity:
        table = read_dishas(tab_id)
        return position_from_table(days, table, radix * u.degree, **kwargs)

    return func


def get_days(date: Date) -> Sexagesimal:
    return Sexagesimal.from_float(date.days_from_epoch(), 0)
