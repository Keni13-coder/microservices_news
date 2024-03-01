from typing import Annotated

from fastapi import Cookie, Depends
from utils import hateoas_dict

from utils.uow.uow_class import IUnitOfWork, UnitOfWork
from utils.security_classes import oauth2_scheme, UserLoginAuth2

UOWDep = Annotated[IUnitOfWork, Depends(UnitOfWork)]

token = Annotated[str, Depends(oauth2_scheme)]

refresh_token_cookie = Annotated[str, Cookie()]

form_data = Annotated[UserLoginAuth2, Depends()]

HateoasDEP = Annotated[list, Depends(hateoas_dict)]