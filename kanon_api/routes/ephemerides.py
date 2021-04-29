from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.routing import APIRouter

from ..core.ephemerides.true_position import moon_true_pos, sun_true_pos
from ..utils import JULIAN_CALENDAR, DateParams, Planet, safe_date

router = APIRouter(prefix="/ephemerides", tags=["ephemerides"])


@router.get("/{planet}/true_pos/")
def get_true_pos(planet: Planet, date_params: DateParams = Depends(DateParams)):

    date = safe_date(JULIAN_CALENDAR, *date_params.ymd)

    if planet == Planet.SUN:
        pos = sun_true_pos(date)

    elif planet == Planet.MOON:
        pos = moon_true_pos(date)

    else:
        raise HTTPException(400, "Not yet implemented")

    return {"value": str(round(pos.value, 2)), "unit": pos.unit.name}
