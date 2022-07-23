from enum import Enum
from functools import partial
from typing import cast

from kanon.units.radices import BasedQuantity, BasedReal

from kanon_api.core.ephemerides.table_classes import TableSet
from kanon_api.utils import build_safe_dict_resolver

from .utils import mod

Houses = tuple[
    BasedReal,
    BasedReal,
    BasedReal,
    BasedReal,
    BasedReal,
    BasedReal,
    BasedReal,
    BasedReal,
    BasedReal,
    BasedReal,
    BasedReal,
    BasedReal,
]


def meth_1(
    table_set: TableSet, ascendant: BasedReal, a0: BasedReal, a1: BasedReal
) -> Houses:
    a2 = mod(a1 + (90 + a0 - a1) / 3)
    a3 = mod(a1 + 2 * (90 + a0 - a1) / 3)
    a12 = mod(a1 - (90 - a0 + a1) / 3)
    a11 = mod(a1 - 2 * (90 - a0 + a1) / 3)
    a10 = mod(a0 - 90)
    a4 = mod(a10 + 180)
    a5 = mod(a11 + 180)
    a6 = mod(a12 + 180)
    a7 = mod(a1 + 180)
    a8 = mod(a2 + 180)
    a9 = mod(a3 + 180)

    return cast(
        Houses,
        (
            ascendant,
            *(
                table_set.RightAscension.reverse_get(x).value
                for x in (a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12)
            ),
        ),
    )


def meth_2(
    table_set: TableSet, ascendant: BasedReal, a0: BasedReal, a1: BasedReal
) -> Houses:

    a10 = mod(-90 + a0)
    a7 = mod(a1 + 180)
    a4 = mod(a10 + 180)

    l10 = table_set.RightAscension.reverse_get(a10).value
    l7 = table_set.RightAscension.reverse_get(a7).value
    l4 = table_set.RightAscension.reverse_get(a4).value

    d0 = mod(l4 - ascendant) / 3
    d1 = mod(l7 - l4) / 3
    d2 = mod(l10 - l7) / 3
    d3 = mod(ascendant - l10) / 3

    return cast(
        Houses,
        tuple(
            mod(x)
            for x in (
                ascendant,
                ascendant + d0,
                ascendant + 2 * d0,
                l4,
                l4 + d1,
                l4 + 2 * d1,
                l7,
                l7 + d2,
                l7 + 2 * d2,
                l10,
                l10 + d3,
                l10 + 2 * d3,
            )
        ),
    )


def meth_5(
    table_set: TableSet, ascendant: BasedReal, a0: BasedReal, a1: BasedReal
) -> Houses:

    return cast(
        Houses,
        (
            ascendant,
            *(
                table_set.RightAscension.reverse_get(mod(a1 + offset + 30)).value
                for offset in range(0, 330, 30)
            ),
        ),
    )


def meth_6(
    table_set: TableSet, ascendant: BasedReal, a0: BasedReal, a1: BasedReal
) -> Houses:

    return cast(Houses, tuple(mod(ascendant + offset) for offset in range(0, 360, 30)))


class HouseMethods(Enum):
    def __call__(
        self, table_set: TableSet, ascendant: BasedQuantity, latitude: float
    ) -> Houses:
        a0 = table_set.ObliqueAscension.get(ascendant, latitude).value
        a1 = table_set.RightAscension.get(ascendant.value).value

        return self.value(table_set, ascendant.value, a0, a1)

    M1 = partial(meth_1)
    M2 = partial(meth_2)
    M5 = partial(meth_5)
    M6 = partial(meth_6)


safe_houses_method = build_safe_dict_resolver(
    {x.name: x for x in HouseMethods},
    "HouseMethods",
    "method",
    "M2",
)
