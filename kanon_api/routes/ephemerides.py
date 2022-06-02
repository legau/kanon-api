import asyncio
from concurrent.futures.process import ProcessPoolExecutor
from functools import partial
from typing import Type

from fastapi.param_functions import Depends, Path, Query
from fastapi.routing import APIRouter
from kanon.calendars import Date
from kanon.units import Sexagesimal

from kanon_api.core.ephemerides.ascendant import ascendant
from kanon_api.core.ephemerides.houses import HouseMethods, safe_houses_method
from kanon_api.core.ephemerides.table_classes import (
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
from kanon_api.core.ephemerides.tables import TableSets
from kanon_api.core.ephemerides.true_position import (
    moon_true_pos,
    planet_true_pos,
    sun_true_pos,
)
from kanon_api.utils import JULIAN_CALENDAR, DateParams, Planet, get_executor, safe_date

router = APIRouter(prefix="/ephemerides/{table_set}", tags=["ephemerides"])

enum_to_class: dict[Planet, Type[CelestialBody]] = {
    Planet.SUN: Sun,
    Planet.MOON: Moon,
    Planet.MARS: Mars,
    Planet.SATURN: Saturn,
    Planet.JUPITER: Jupiter,
    Planet.MERCURY: Mercury,
    Planet.VENUS: Venus,
}


def compute_true_pos(
    table_set_name: str, planet_class: Type[CelestialBody], days: float
):

    planet = TableSets(table_set_name)(planet_class)

    if isinstance(planet, Sun):
        func = partial(sun_true_pos, table_set=planet.tset)

    elif isinstance(planet, Moon):
        func = partial(moon_true_pos, table_set=planet.tset)

    elif isinstance(planet, SuperiorPlanet):
        func = partial(
            planet_true_pos,
            planet=planet,
        )

    else:
        raise NotImplementedError

    return str(round(func(days=days).value, 2))


def get_planet_with_set(table_set: TableSets = Path(...), planet: Planet = Path(...)):
    return table_set.name, enum_to_class[planet]


async def run_compute_pos(
    executor, table_set: str, planet: Type[CelestialBody], date: Date
):
    return (
        date.jdn,
        await asyncio.get_running_loop().run_in_executor(
            executor,
            compute_true_pos,
            table_set,
            planet,
            date.days_from_epoch(),
        ),
    )


@router.get("/{planet}/true_pos/")
async def get_true_pos(
    planet_with_set: tuple[str, Type[CelestialBody]] = Depends(get_planet_with_set),
    date_params: DateParams = Depends(),
    number_of_values: int = Query(1, ge=1),
    step: int = Query(1, ge=1),
    executor: ProcessPoolExecutor = Depends(get_executor),
):

    start_date = safe_date(JULIAN_CALENDAR, date_params)

    dates = (start_date + i for i in range(0, number_of_values * step, step))

    results = await asyncio.gather(
        *(run_compute_pos(executor, *planet_with_set, date) for date in dates)
    )

    return [{"jdn": jdn, "position": position} for jdn, position in results]


@router.get("/ascendant/")
def get_ascendant(
    table_set: TableSets = Path(...),
    latitude: float = Query(..., ge=-90, le=90),
    date_params: DateParams = Depends(),
):

    date = safe_date(JULIAN_CALENDAR, date_params)

    pos = ascendant(table_set, date.days_from_epoch(), latitude)

    return {"value": str(round(Sexagesimal(pos.value, 2)))}


@router.get("/houses/")
def get_houses(
    table_set: TableSets = Path(...),
    method: HouseMethods = Depends(safe_houses_method),
    latitude: float = Query(..., ge=-90, le=90),
    date_params: DateParams = Depends(),
):

    date = safe_date(JULIAN_CALENDAR, date_params)

    asc = ascendant(table_set, date.days_from_epoch(), latitude)

    houses_list = method(table_set, asc, latitude)

    return [str(round(Sexagesimal(x, 2))) for x in houses_list]
