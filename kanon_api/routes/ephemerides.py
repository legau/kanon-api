import asyncio
from concurrent.futures.process import ProcessPoolExecutor
from functools import partial
from typing import Type, cast

from fastapi.param_functions import Depends, Query
from fastapi.routing import APIRouter
from kanon.units import Sexagesimal

from kanon_api.core.ephemerides.ascendant import ascendant
from kanon_api.core.ephemerides.tables import (
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
from kanon_api.core.ephemerides.true_position import (
    moon_true_pos,
    planet_true_pos,
    sun_true_pos,
)
from kanon_api.utils import JULIAN_CALENDAR, DateParams, Planet, get_executor, safe_date

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


def compute_true_pos(planet: Planet, days: float):

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

    return str(round(func(days).value, 2))


@router.get("/{planet}/true_pos/")
async def get_true_pos(
    planet: Planet,
    date_params: DateParams = Depends(DateParams),
    number_of_values: int = Query(1, ge=1),
    step: int = Query(1, ge=1),
    executor: ProcessPoolExecutor = Depends(get_executor),
):

    start_date = safe_date(JULIAN_CALENDAR, date_params)

    dates = (start_date + i for i in range(0, number_of_values * step, step))

    loop = asyncio.get_running_loop()

    results = [
        (
            date.jdn,
            loop.run_in_executor(
                executor, compute_true_pos, planet, date.days_from_epoch()
            ),
        )
        for date in dates
    ]

    return [
        {"jdn": jdn, "position": await result_awaitable}
        for jdn, result_awaitable in results
    ]


@router.get("/ascendant/")
def get_ascendant(
    latitude: float = Query(..., ge=-90, le=90),
    date_params: DateParams = Depends(DateParams),
):

    date = safe_date(JULIAN_CALENDAR, date_params)

    pos = ascendant(date.days_from_epoch(), latitude)

    return {"value": str(round(Sexagesimal(pos.value, 2)))}
