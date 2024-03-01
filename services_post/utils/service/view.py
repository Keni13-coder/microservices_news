from typing import List

from fastapi import HTTPException
from uuid import UUID

from sqlalchemy.exc import NoResultFound, IntegrityError

from schemas import (
    CreateViewSchema, 
    OutputViewSchema, 
    )
    
from utils.uow.uow_class import IUnitOfWork
'посмотерть что делает ошибка IntegrityError'

class ViewService:
    async def view_add(self, view_data: CreateViewSchema, uow: IUnitOfWork, owner_uid: UUID) -> None:
        data = view_data.model_dump()
        data['owner_uid'] = owner_uid
        async with uow:
            try:
                await uow.view.add_one(data)
                await uow.commit()
                
            except IntegrityError:
                pass

    async def get_view_all(self, post_uid: UUID, uow: IUnitOfWork) -> List[OutputViewSchema]:
        async with uow:
            try:
                views = await uow.view.find_all(post_uid=post_uid) 
            
            except NoResultFound:
                er = {'type': 'value_error', 'loc': (), 'msg': "Value error, 'View not found' is not a valid HTTPStatus", 'input': {}}
                raise HTTPException(status_code=412, detail=er)
            
        return views
    
    
    
view_service = ViewService()