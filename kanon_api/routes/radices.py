from typing import Type

from fastapi.param_functions import Depends, Query
from fastapi.routing import APIRouter, HTTPException
from kanon.units.radices import BasedReal

from ..utils import safe_radix

router = APIRouter(prefix="/radices", tags=["radices"])


@router.get("/{radix}/from_float/")
def get_from_float(
    *,
    radix: Type[BasedReal] = Depends(safe_radix),
    value: float,
    precision: int = 3,
):

    return {"value": str(radix.from_float(value, precision)), "type": radix.__name__}


@router.get("/{radix}/to_float/")
def get_to_float(
    radix: Type[BasedReal] = Depends(safe_radix),
    value: str = Query(..., min_length=1),
):

    try:
        return {"value": float(radix(value))}
    except (ValueError, TypeError) as err:
        raise HTTPException(400, str(err))
