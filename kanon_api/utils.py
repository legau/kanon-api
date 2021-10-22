import inspect
from concurrent.futures.process import ProcessPoolExecutor
from enum import Enum
from typing import TypeVar, no_type_check

from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Query
from kanon.calendars import Calendar, Date
from kanon.units import radix_registry

JULIAN_CALENDAR = Calendar.registry["Julian A.D."]


def safe_date(calendar: Calendar, date: "DateParams") -> Date:
    try:
        return Date(calendar, date.ymd, date.hours + date.minutes / 60)
    except ValueError as err:
        raise HTTPException(400, str(err))


class DateParams:
    def __init__(
        self,
        year: int,
        month: int = Query(..., ge=1),
        day: int = Query(..., ge=1),
        hours: int = Query(12, ge=0, lt=24),
        minutes: int = Query(0, ge=0, lt=60),
    ):
        self.year = year
        self.month = month
        self.day = day
        self.hours = hours
        self.minutes = minutes

    @property
    def ymd(self):
        return (self.year, self.month, self.day)


class StrEnum(str, Enum):
    pass


T = TypeVar("T")


@no_type_check
def build_safe_dict_resolver(target: dict[str, T], name: str, param_name: str):
    enum = StrEnum(name, {k: k for k in target.keys()})

    param = inspect.Parameter(
        param_name, inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=enum
    )

    def func(**kwargs: enum) -> T:
        return target[kwargs[param_name].value]

    func.__signature__ = inspect.signature(func).replace(parameters=[param])

    return func


safe_calendar = build_safe_dict_resolver(
    Calendar.registry, "SupportedCalendars", "calendar"
)

safe_radix = build_safe_dict_resolver(radix_registry, "SupportedRadices", "radix")


class Planet(StrEnum):
    SUN = "sun"
    MOON = "moon"
    MARS = "mars"
    VENUS = "venus"
    JUPITER = "jupiter"
    MERCURY = "mercury"
    SATURN = "saturn"


def get_executor(request: Request) -> ProcessPoolExecutor:
    return request.app.state.executor


class StaticMeta(type):
    def __call__(cls, *args, **kwargs):
        raise TypeError(f"Can't instantiate static class {cls.__name__}")
