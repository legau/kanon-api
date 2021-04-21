from fastapi.exceptions import HTTPException
from kanon.calendars import Calendar, Date

JULIAN_CALENDAR = Calendar.registry["Julian A.D."]


def safe_calendar(name: str) -> Calendar:
    try:
        return Calendar.registry[name]
    except KeyError as err:
        raise HTTPException(400, str(err))


def safe_date(calendar: Calendar, year: int, month: int, day: int) -> Date:
    try:
        return Date(calendar, (year, month, day))
    except ValueError as err:
        raise HTTPException(400, str(err))
