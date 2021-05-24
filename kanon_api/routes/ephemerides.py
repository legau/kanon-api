from functools import partial
from typing import Type, cast

from fastapi.param_functions import Depends, Query
from fastapi.routing import APIRouter

from ..core.ephemerides.ascendant import ascendant
from ..core.ephemerides.tables import (
    CelestialBody,
    Jupiter,
    Mars,
    Mercury,
    Moon,
    Saturn,
    Sun,
    SuperiorPlanet,
    Venus,
)
from ..core.ephemerides.true_position import (
    moon_true_pos,
    planet_true_pos,
    sun_true_pos,
)
from ..utils import JULIAN_CALENDAR, DateParams, Planet, safe_date

router = APIRouter(prefix="/ephemerides", tags=["ephemerides"])

enum_to_class: dict[Planet, Type[CelestialBody]] = {
    Planet.SUN: Sun,
    Planet.MOON: Moon,
    Planet.MARS: Mars,
    Planet.SATURN: Saturn,
    Planet.JUPITER: Jupiter,
    Planet.MERCURY: Mercury,
    Planet.VENUS: Venus,
}


@router.get("/{planet}/true_pos/")
def get_true_pos(
    planet: Planet,
    date_params: DateParams = Depends(DateParams),
    number_of_values: int = Query(1, ge=1),
    step: int = Query(1, ge=1),
):

    start_date = safe_date(JULIAN_CALENDAR, *date_params.ymd)

    if planet == Planet.SUN:
        func = sun_true_pos

    elif planet == Planet.MOON:
        func = moon_true_pos

    elif planet in enum_to_class:
        func = partial(
            planet_true_pos, planet=cast(Type[SuperiorPlanet], enum_to_class[planet])
        )

    else:
        raise NotImplementedError

    dates = (start_date + i for i in range(0, number_of_values * step, step))

    return [
        {
            "jdn": date.jdn,
            "position": str(round(func(date.days_from_epoch()).value, 2)),
        }
        for date in dates
    ]


@router.get("/ascendant/")
def get_ascendant(date_params: DateParams = Depends(DateParams)):

    date = safe_date(JULIAN_CALENDAR, *date_params.ymd)

    pos = ascendant(date.days_from_epoch())

    return {"value": str(round(pos.value, 2))}
