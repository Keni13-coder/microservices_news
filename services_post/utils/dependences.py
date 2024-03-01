from typing import Annotated

from fastapi import Cookie, Depends
from pydantic import UUID4

from utils import hateoas_dict
from utils.uow.uow_class import IUnitOfWork, UnitOfWork
from schemas import (
    CreateImage,
    UpgradeImage,
    CreatePostClass,
    UpgradePostClass)

UOWDep = Annotated[IUnitOfWork, Depends(UnitOfWork)]
image = Annotated[CreateImage, Depends()]
uprage_image = Annotated[UpgradeImage, Depends()]


token_cookie = Annotated[UUID4 | None, Cookie()]
CreatePost = Annotated[CreatePostClass, Depends()]
UpgradePost = Annotated[UpgradePostClass, Depends()]

HateoasDEP = Annotated[list, Depends(hateoas_dict)]




