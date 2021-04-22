from fastapi.param_functions import Depends
from fastapi.routing import APIRouter
from kanon.calendars.calendars import Calendar

from kanon_api.utils import DateParams, safe_calendar, safe_date

router = APIRouter(prefix="/calendars", tags=["calendars"])


@router.get("/{calendar}/to_jdn/")
def get_to_jdn(
    calendar: Calendar = Depends(safe_calendar),
    date_params: DateParams = Depends(),
):

    date = safe_date(calendar, *date_params.ymd)

    return {"jdn": date.jdn}


@router.get("/{calendar}/from_jdn/")
def get_from_jdn(jdn: float, calendar: Calendar = Depends(safe_calendar)):

    date = calendar.from_julian_days(jdn)

    return {"date": str(date), "ymd": date.ymd}
