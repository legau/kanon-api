from fastapi import FastAPI, HTTPException
from kanon.calendars.calendars import Calendar, Date

from kanon_api.ephemerides.sun import sun_true_pos

app = FastAPI()

julian_cal = Calendar.registry["Julian A.D."]


@app.get("/sun_true_pos/")
def get_sun_true_pos(year: int, month: int, day: int):

    try:
        date = Date(julian_cal, (year, month, day))
    except ValueError as err:
        raise HTTPException(400, str(err))

    pos = sun_true_pos(date)

    return {"value": str(round(pos.value, 2)), "unit": pos.unit.name}
