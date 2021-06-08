from enum import Enum
from typing import Type

from fastapi.param_functions import Depends, Path, Query
from fastapi.routing import APIRouter, HTTPException
from kanon.units.radices import BasedReal, IllegalBaseValueError

from kanon_api.core.calculations.parser import parse

from ..utils import safe_radix

router = APIRouter(prefix="/calculations", tags=["calculations"])


def based_real_response(br: BasedReal):
    return {"value": str(br.truncate()), "remainder": str(br.remainder)}


@router.get("/{radix}/from_float/")
def get_from_float(
    *,
    radix: Type[BasedReal] = Depends(safe_radix),
    value: float,
    precision: int = 3,
):

    return {
        **based_real_response(radix.from_float(value, precision)),
        "type": radix.__name__,
    }


@router.get("/{radix}/to_float/")
def get_to_float(
    radix: Type[BasedReal] = Depends(safe_radix),
    value: str = Query(..., min_length=1),
):

    try:
        return {"value": float(radix(value))}
    except (ValueError, TypeError) as err:
        raise HTTPException(400, str(err))


@router.get("/{radix}/compute/")
def get_compute(
    radix: Type[BasedReal] = Depends(safe_radix),
    query: str = Query(..., min_length=1),
):

    try:
        return based_real_response(parse(query, radix))
    except (SyntaxError, IllegalBaseValueError) as err:
        raise HTTPException(400, str(err))


class Operation(str, Enum):
    add = "add"
    sub = "sub"
    mul = "mul"
    div = "div"


op_to_token = {
    Operation.add: "+",
    Operation.sub: "-",
    Operation.mul: "*",
    Operation.div: "/",
}


@router.get("/{radix}/{operation}/{a}/{b}/")
def get_operation(
    operation: Operation,
    radix: Type[BasedReal] = Depends(safe_radix),
    a: str = Path(..., min_length=1),
    b: str = Path(..., min_length=1),
):

    try:
        return based_real_response(parse(f"{a}{op_to_token[operation]}{b}", radix))
    except (SyntaxError, IllegalBaseValueError) as err:
        raise HTTPException(400, str(err))
