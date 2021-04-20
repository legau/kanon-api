from fastapi import FastAPI, HTTPException
from kanon.units import Sexagesimal

from kanon_api.ephemerides.sun import sun_true_pos
from kanon_api.utils import JULIAN_CALENDAR, safe_calendar, safe_date

app = FastAPI()


@app.get("/sun_true_pos/")
def get_sun_true_pos(year: int, month: int, day: int):

    date = safe_date(JULIAN_CALENDAR, year, month, day)
    pos = sun_true_pos(date)

    return {"value": str(round(pos.value, 2)), "unit": pos.unit.name}


@app.get("/date_jdn/")
def get_date_jdn(calendar: str, year: int, month: int, day: int):

    cal = safe_calendar(calendar)
    date = safe_date(cal, year, month, day)

    return {"jdn": date.jdn}


@app.get("/jdn_date/")
def get_jdn_date(calendar: str, jdn: float):

    cal = safe_calendar(calendar)
    date = cal.from_julian_days(jdn)

    return {"date": date.ymd}


@app.get("/float_sexa/")
def get_float_sexa(value: float, precision: int = 3):

    return {"value": str(Sexagesimal.from_float(value, precision))}


@app.get("/sexa_float/")
def get_sexa_float(value: str):

    try:
        return {"value": float(Sexagesimal(value))}
    except (ValueError, TypeError) as err:
        raise HTTPException(400, str(err))
