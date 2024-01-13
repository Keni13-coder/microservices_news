from typing import Annotated

from fastapi import Depends

from db.utils.uow_class import IUnitOfWork, UnitOfWork
from services.user_service import current_user, UOWDep, UserService, user_service
from services.post_service import post_service, comment_service, recent, popular

current_user = Annotated[UserService, Depends(current_user)]



