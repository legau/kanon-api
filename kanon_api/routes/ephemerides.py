from typing import Type, cast

from fastapi.param_functions import Depends
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
        pos = sun_true_pos(date)

    elif planet == Planet.MOON:
        pos = moon_true_pos(date)

    elif planet in enum_to_class:
        pos = planet_true_pos(date, cast(Type[SuperiorPlanet], enum_to_class[planet]))

    else:
        raise NotImplementedError

    return {"value": str(round(pos.value, 2)), "unit": pos.unit.name}


@router.get("/ascendant/")
def get_ascendant(date_params: DateParams = Depends(DateParams)):

    date = safe_date(JULIAN_CALENDAR, *date_params.ymd)

    pos = ascendant(date)

    return {"value": str(round(pos.value, 2)), "unit": pos.unit.name}
