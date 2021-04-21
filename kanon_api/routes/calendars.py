from fastapi.routing import APIRouter

from kanon_api.utils import safe_calendar, safe_date

router = APIRouter(prefix="/calendars", tags=["calendars"])


@router.get("/date_jdn/")
def get_date_jdn(calendar: str, year: int, month: int, day: int):

    cal = safe_calendar(calendar)
    date = safe_date(cal, year, month, day)

    return {"jdn": date.jdn}


@router.get("/jdn_date/")
def get_jdn_date(calendar: str, jdn: float):

    cal = safe_calendar(calendar)
    date = cal.from_julian_days(jdn)

    return {"date": date.ymd}
