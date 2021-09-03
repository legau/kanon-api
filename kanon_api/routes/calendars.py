import dataclasses

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

    date = safe_date(calendar, date_params)

    return {"jdn": date.jdn, "date": str(date)}


@router.get("/{calendar}/from_jdn/")
def get_from_jdn(jdn: float, calendar: Calendar = Depends(safe_calendar)):

    date = calendar.from_julian_days(jdn)

    return {"date": str(date), "ymd": date.ymd, "frac": date.frac}


@router.get("/{calendar}/infos")
def get_infos(calendar: Calendar = Depends(safe_calendar)):

    return {
        "common_year": calendar.common_year,
        "leap_year": calendar.leap_year,
        "months": [dataclasses.asdict(m) for m in calendar.months],
        "name": calendar.name,
        "cycle": calendar.cycle,
        "era": calendar.era.epoch,
    }
