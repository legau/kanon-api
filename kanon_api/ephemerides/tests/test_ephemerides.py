from kanon.calendars import Calendar, Date
from kanon.units import Sexagesimal

from kanon_api.ephemerides.sun import sun_true_pos


def test_true_sun():
    calendar = Calendar.registry["Julian A.D."]

    date = Date(calendar, (1327, 7, 3))

    res = sun_true_pos(date)
    assert round(res.value, 2) == Sexagesimal("1,47;18,48")
