import pytest
from kanon.calendars import Calendar, Date
from kanon.units import Sexagesimal

from kanon_api.core.ephemerides.ascendant import ascendant
from kanon_api.core.ephemerides.tables import Jupiter, Mars, Mercury, Saturn, Venus
from kanon_api.core.ephemerides.true_position import (
    moon_true_pos,
    planet_true_pos,
    sun_true_pos,
)

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
        ((10, 2, 13), "01,14 ; 42,27"),
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
    ],
)
def test_planet_true_pos(planet, ymd, result):
    date = Date(julian_calendar, ymd)

    res = planet_true_pos(date.days_from_epoch(), planet)
    assert round(res.value, 2) == Sexagesimal(result)


@pytest.mark.parametrize(
    "date, result",
    [
        ((1327, 7, 3), "3,15;0,3"),
        ((10, 2, 13), "1,16;48,56"),
    ],
)
def test_ascendant(date, result):
    degree_ascension = ascendant(Date(julian_calendar, date).days_from_epoch())

    assert round(degree_ascension.value, 2) == Sexagesimal(result)
