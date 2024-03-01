from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
import pydantic
import json
from typing import Any

async def redis_encode(data: pydantic.BaseModel):
    data = data.model_dump_json().encode()
    return data





async def redis_decode(encode_str: str, execution_model: pydantic.BaseModel):
    try:
        resul = execution_model.model_validate_json(encode_str)
    except pydantic.ValidationError as e:
        raise HTTPException(
                detail=jsonable_encoder(e.errors()),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
    return resul





class Singleton:
    """A class to implement the Singleton design pattern.

    Attributes:
        _instance : the single instance of the class

    Methods:
        __new__ : creates a new instance of the class if it doesn't exist, otherwise returns the existing instance
        _drop : sets the instance to None, allowing a new instance to be created
    """

    _instance = None

    def __new__(cls, *args: Any, **kwargs: Any) -> "Singleton":
        """Create a singleton instance of a class.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            The singleton instance of the class
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def _drop(cls) -> None:
        """Drop the instance of a class.

        Returns:
            None
        """
        cls._instance = None