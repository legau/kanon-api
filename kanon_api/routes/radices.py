from fastapi.routing import APIRouter, HTTPException
from kanon.units import Sexagesimal

router = APIRouter(prefix="/radices", tags=["radices"])


@router.get("/float_sexa/")
def get_float_sexa(value: float, precision: int = 3):

    return {"value": str(Sexagesimal.from_float(value, precision))}


@router.get("/sexa_float/")
def get_sexa_float(value: str):

    try:
        return {"value": float(Sexagesimal(value))}
    except (ValueError, TypeError) as err:
        raise HTTPException(400, str(err))
