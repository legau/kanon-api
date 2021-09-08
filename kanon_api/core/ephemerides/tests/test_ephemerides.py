import pytest
from kanon.calendars import Calendar, Date
from kanon.units import Sexagesimal

from kanon_api.core.ephemerides.ascendant import ascendant, houses
from kanon_api.core.ephemerides.tables import Jupiter, Mars, Mercury, Saturn, Venus
from kanon_api.core.ephemerides.true_position import (
    moon_true_pos,
    planet_true_pos,
    sun_true_pos,
)
from kanon_api.units import degree

julian_calendar = Calendar.registry["Julian A.D."]


@pytest.mark.parametrize(
    "ymd, result",
    [
        ((1327, 7, 3), "1,47;18,48"),
        ((10, 2, 13), "05,22 ; 36,47"),
    ],
)
def test_true_sun(ymd, result):
    date = Date(julian_calendar, ymd)

    res = sun_true_pos(date.days_from_epoch())
    assert round(res.value, 2) == Sexagesimal(result)


@pytest.mark.parametrize(
    "ymd, result",
    [
        ((1327, 7, 3), "4,19;35,55"),
        ((1403, 3, 12), "3,28;15,28"),
        ((10, 2, 13), "01,14 ; 42,27"),
        ((1327, 7, 11), "5,57 ; 18,24"),
    ],
)
def test_true_moon(ymd, result):
    date = Date(julian_calendar, ymd)

    res = moon_true_pos(date.days_from_epoch())
    assert round(res.value, 2) == Sexagesimal(result)


@pytest.mark.parametrize(
    "planet, ymd, result",
    [
        (Mars, (1327, 7, 3), "2,14;52,23"),
        (Mars, (10, 2, 13), "5,41;36,30"),
        (Saturn, (1327, 7, 3), "1,47;5,1"),
        (Jupiter, (1327, 7, 3), "2,14;35,29"),
        (Mercury, (1327, 7, 3), "2,13;5,1"),
        (Venus, (1327, 7, 3), "2,1;27,13"),
        (Venus, (7, 2, 23), "1;6,18"),
        (Mercury, (7, 3, 26), "5,39 ; 06,40"),
    ],
)
def test_planet_true_pos(planet, ymd, result):
    date = Date(julian_calendar, ymd)

    res = planet_true_pos(date.days_from_epoch(), planet)
    assert round(res.value, 2) == Sexagesimal(result)


@pytest.mark.parametrize(
    "date, hours, latitude, result",
    [
        ((1327, 7, 3), 0.5, 31, "03,16 ; 11,46"),
        ((1327, 7, 3), 0.6, 31, "03,46 ; 35,49"),
        ((10, 2, 13), 0.5, 43, "01,19 ; 32,23"),
        ((10, 2, 13), 0.5, 30, "01,10 ; 36,09"),
        ((10, 2, 13), 0.5, 10, "01,03 ; 24,58"),
        ((10, 2, 13), 0.5, 49, "01,24 ; 46,20"),
        ((10, 2, 13), 0.5, 48, "01,24 ; 46,20"),
    ],
)
def test_ascendant(date, hours, latitude, result):
    degree_ascension = ascendant(
        Date(julian_calendar, date, hours).days_from_epoch(), latitude
    )

    assert round(Sexagesimal(degree_ascension.value, 2), 2) == Sexagesimal(result)


def test_houses():
    asc = 236 + Sexagesimal("0;38")

    h = houses(asc * degree, float(Sexagesimal("39;51")))
    assert round(h[2].value) == Sexagesimal("05,07 ; 28")
