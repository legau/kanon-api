from fastapi.routing import APIRouter

from kanon_api.core.ephemerides.sun import sun_true_pos
from kanon_api.utils import JULIAN_CALENDAR, safe_date

router = APIRouter(prefix="/ephemerides", tags=["ephemerides"])


@router.get("/sun_true_pos/")
def get_sun_true_pos(year: int, month: int, day: int):

    date = safe_date(JULIAN_CALENDAR, year, month, day)
    pos = sun_true_pos(date)

    return {"value": str(round(pos.value, 2)), "unit": pos.unit.name}
