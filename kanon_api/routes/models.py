import warnings
from collections import OrderedDict
from typing import Any, Literal

import numpy as np
from fastapi import HTTPException
from fastapi.param_functions import Depends, Path
from fastapi.routing import APIRouter
from kanon.models.meta import ModelCallable, get_model_by_id
from pydantic import BaseModel, root_validator, validator
from scipy import optimize

router = APIRouter(prefix="/models", tags=["models"])


def model_path(model: int = Path(...)) -> ModelCallable:
    try:
        return get_model_by_id(model)
    except (KeyError, ValueError):
        raise HTTPException(status_code=404, detail="Model not found")


class ModelInfos(BaseModel):
    args: Literal[1, 2]
    params: tuple[int, ...]
    table_type: str
    table_type_id: int
    model_name: str


@router.get("/{model}/", response_model=ModelInfos)
def get_model(model: ModelCallable = Depends(model_path)):
    return {
        "args": model.args,
        "params": model.params,
        "table_type": model.table_type.name,
        "table_type_id": model.table_type.value,
        "model_name": model.__name__,
    }


class TableContent(BaseModel):
    arg1: list[float]
    params: dict[int, float | None]
    displacement: list[float] = [
        0,
        0,
        0,
    ]  # (Entries, Arg1, Arg2)
    arg2: list[float] | None = None
    model: ModelCallable = Depends(model_path)

    @validator("displacement")
    def check_displacement(cls, v):
        if len(v) != 3:
            raise HTTPException(
                status_code=400, detail="Displacement array must have 3 elements"
            )
        return v

    @validator("arg1", "arg2")
    def check_not_empty(cls, v):
        if v is not None and len(v) == 0:
            raise HTTPException(status_code=400, detail="Arguments cannot be empty")
        return v

    @root_validator
    def check_model(cls, values: dict[str, Any]):
        params: list[float] = values["params"]
        arg2: list[float] | None = values.get("arg2")
        model: ModelCallable = values["model"]

        if set(model.params) != set(params):
            raise HTTPException(
                status_code=400, detail=f"Invalid parameters, {model.params}"
            )

        if arg2 is None and model.args == 1 or arg2 and model.args == 2:
            return values

        raise HTTPException(status_code=400, detail="Invalid number of arguments")

    @property
    def ordered_params(self):
        return OrderedDict({p: self.params[p] for p in self.model.params})

    def __call__(self, *args):
        displaced_args = args[: 2 if self.arg2 else 1]
        return (
            self.model(*displaced_args, *args[len(displaced_args) :])  # noqa: E203
            + self.displacement[0]
        )

    def __len__(self):
        if self.arg2:
            return len(self.arg1) * len(self.arg2)
        return len(self.arg1)

    class Config:
        arbitrary_types_allowed = True


@router.post("/{model}/fill/", response_model=list[float])
def fill_by_model(content: TableContent = Depends()):
    params = content.ordered_params.values()
    if None in params:
        raise HTTPException(400, detail="Null parameter")
    if content.arg2:
        return [content(a1, a2, *params) for a2 in content.arg2 for a1 in content.arg1]
    return [content(a1, *params) for a1 in content.arg1]


@router.post("/{model}/estimate/", response_model=dict[int, float])
def estimate_parameter(
    entries: list[float],
    content: TableContent = Depends(),
):
    if len(content) != len(entries):
        raise HTTPException(
            status_code=400, detail="Number of entries does not match arguments"
        )
    if None not in content.params.values():
        raise HTTPException(status_code=400, detail="No parameter to estimate")

    def params(parameters: tuple[float, ...]):
        iter_parameters = iter(parameters)
        return [
            p if p is not None else next(iter_parameters)
            for p in content.ordered_params.values()
        ]

    if content.arg2:
        arguments = np.array([[a, b] for b in content.arg2 for a in content.arg1])

        def optim_model(args: list, *parameters: float):
            return np.array([content(*arg, *params(parameters)) for arg in args])

    else:
        arguments = np.array(content.arg1)

        def optim_model(args: list, *parameters: float):
            return np.array([content(arg, *params(parameters)) for arg in args])

    keys = [k for k, v in content.ordered_params.items() if v is None]

    with warnings.catch_warnings():
        try:
            popt, _ = optimize.curve_fit(
                optim_model, arguments, np.array(entries), [1] * len(keys)
            )
        except TypeError as err:  # pragma: no cover
            raise HTTPException(status_code=400, detail=str(err))

    return zip(keys, popt)
