import inspect
from concurrent.futures.process import ProcessPoolExecutor
from enum import Enum
from typing import Type, TypeVar, no_type_check

import kanon.units.definitions as definitions
from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Query
from kanon.calendars import Calendar, Date
from kanon.units import BasedReal

from . import settings

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
def build_safe_dict_resolver(
    target: dict[str, T],
    name: str,
    param_name: str,
    default: str | Type[inspect.Parameter.empty] = inspect.Parameter.empty,
):
    enum = StrEnum(name, {k: k for k in target.keys()})

    if isinstance(default, str):

        class Default(str):
            value = default

        default = Default(default)

    param = inspect.Parameter(
        param_name,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        annotation=enum,
        default=default,
    )

    def func(**kwargs: enum) -> T:
        return target[kwargs[param_name].value]

    func.__signature__ = inspect.signature(func).replace(parameters=[param])

    return func


safe_calendar = build_safe_dict_resolver(
    Calendar.registry, "SupportedCalendars", "calendar"
)

safe_radix = build_safe_dict_resolver(
    {
        x.__name__: x
        for x in definitions.__dict__.values()
        if inspect.isclass(x) and issubclass(x, BasedReal) and x is not BasedReal
    },
    "SupportedRadices",
    "radix",
)


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


class DeferedMeta(type):
    def __call__(cls, *args, **kwargs):
        if settings.PRODUCTION:
            return super().__call__(*args, **kwargs)

        def init_before_get(obj, attr):
            try:
                if not object.__getattribute__(obj, "_initialized"):
                    obj._initialized = True
                    object.__getattribute__(obj, "__init__")(*args, **kwargs)
            except AttributeError:
                pass
            return object.__getattribute__(obj, attr)

        cls.__getattribute__ = init_before_get

        new_obj = cls.__new__(cls, *args, **kwargs)
        new_obj._initialized = False
        return new_obj
