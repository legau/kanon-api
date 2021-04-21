import pytest
from kanon.calendars import Calendar, Date
from kanon.units import Sexagesimal

from kanon_api.core.ephemerides.sun import sun_true_pos


@pytest.mark.parametrize(
    "ymd, result",
    [
        ((1327, 7, 3), "1,47;18,48"),
        ((10, 2, 13), "05,22 ; 36,47"),
    ],
)
def test_true_sun(ymd, result):
    calendar = Calendar.registry["Julian A.D."]

    date = Date(calendar, ymd)

    res = sun_true_pos(date)
    assert round(res.value, 2) == Sexagesimal(result)
