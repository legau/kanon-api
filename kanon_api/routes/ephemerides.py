from typing import Type, cast

from fastapi.param_functions import Depends, Query
from fastapi.routing import APIRouter

from kanon_api.core.ephemerides.ascendant import ascendant

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
def get_true_pos(planet: Planet, date_params: DateParams = Depends(DateParams)):

    date = safe_date(JULIAN_CALENDAR, *date_params.ymd)

    if planet == Planet.SUN:
        pos = sun_true_pos(date.days_from_epoch())

    elif planet == Planet.MOON:
        pos = moon_true_pos(date.days_from_epoch())

    elif planet in enum_to_class:
        pos = planet_true_pos(
            date.days_from_epoch(), cast(Type[SuperiorPlanet], enum_to_class[planet])
        )

    else:
        raise NotImplementedError

    return {"value": str(round(pos.value, 2)), "unit": pos.unit.name}


@router.get("/ascendant/")
def get_ascendant(date_params: DateParams = Depends(DateParams)):

    date = safe_date(JULIAN_CALENDAR, *date_params.ymd)

    pos = ascendant(date.days_from_epoch())

    return {"value": str(round(pos.value, 2)), "unit": pos.unit.name}


@router.get("/{planet}/ephemerides")
def get_ephemerides(
    planet: Planet,
    date_params: DateParams = Depends(DateParams),
    number_of_values: int = Query(..., ge=1),
    step: int = Query(..., ge=1),
):
    start_date = safe_date(JULIAN_CALENDAR, *date_params.ymd)

    dates = (start_date + i for i in range(0, number_of_values * step, step))

    return [{
        "jdn": date.jdn,
        "position": get_true_pos(planet, date)["value"]
    } for date in dates]
