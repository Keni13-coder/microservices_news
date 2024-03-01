import dataclasses
import inspect
from typing import Type
import pydantic
from fastapi import Form, HTTPException, status
from fastapi.encoders import jsonable_encoder



def as_form(cls: Type[pydantic.BaseModel]):
    cls.__signature__ = cls.__signature__.replace(
        parameters=[
            arg.replace(default=Form(...))
            for arg in cls.__signature__.parameters.values()
        ]
    )
    return cls



class Checker:
    def __init__(self, model: pydantic.BaseModel):
        self.model = model

    def __call__(self, data = Form(...)):
        try:
            return self.model.model_validate_json(data)
        except pydantic.ValidationError as e:
            raise HTTPException(
                detail=jsonable_encoder(e.errors()),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
            

