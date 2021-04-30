from fastapi.param_functions import Depends
from fastapi.routing import APIRouter

from ..core.ephemerides.tables import Jupiter, Mars, Mercury, Moon, Saturn, Sun, Venus
from ..core.ephemerides.true_position import (
    moon_true_pos,
    outer_planet_true_pos,
    sun_true_pos,
)
from ..utils import JULIAN_CALENDAR, DateParams, Planet, safe_date

router = APIRouter(prefix="/ephemerides", tags=["ephemerides"])

enum_to_class = {
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

    elif planet in (Planet.MARS, Planet.SATURN, Planet.JUPITER):
        pos = outer_planet_true_pos(date, enum_to_class[planet])

    else:
        raise NotImplementedError

    return {"value": str(round(pos.value, 2)), "unit": pos.unit.name}
