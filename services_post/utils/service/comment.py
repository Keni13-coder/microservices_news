from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound

from utils.uow.uow_class import IUnitOfWork
from schemas import (
    CreateCommentSchema, 
    UpgradeCommentSchema,
    OutputCommentSchema, 
)



class CommentService:

    async def add_comment(self, comment: CreateCommentSchema, uow: IUnitOfWork, owner_uid: UUID) -> OutputCommentSchema:
        add_data = comment.model_dump()
        add_data['owner_uid'] = owner_uid
        
        async with uow:
            comment = await uow.comment.add_one(add_data)
            await uow.commit()
        return comment
    
    async def get_comment_all(self, post_uid: UUID, uow: IUnitOfWork) -> List[OutputCommentSchema]:
        async with uow:
            try:
                comments = await uow.comment.find_all(post_uid=post_uid)
            except NoResultFound:
                er = {'type': 'value_error', 'loc': (), 'msg': "Value error, 'Comments not found' is not a valid HTTPStatus", 'input': {}}
                raise HTTPException(status_code=412, detail=er)
            
        return comments
        
    
    async def delete_comment(self, comment_uid: UUID, uow: IUnitOfWork, owner_uid: UUID) -> None:
        async with uow:
            try:
                await uow.comment.deactivate_one(comment_uid, uid_user=owner_uid)
                await uow.commit()
            except NoResultFound:
                er = {'type': 'value_error', 'loc': (), 'msg': "Value error, 'Comments not found' is not a valid HTTPStatus", 'input': {}}
                raise HTTPException(status_code=412, detail=er)
            
    async def delete_comment_all(self,  post_uid: UUID, uow: IUnitOfWork, owner_uid: UUID) -> None:
        # возможна ошибки завязынные на ретурне uid тк у нас будет список
        async with uow:
            try:
                await uow.comment.deactivate_all(post_uid, owner_uid=owner_uid)
                await uow.commit()
            except NoResultFound:
                er = {'type': 'value_error', 'loc': (), 'msg': "Value error, 'Comments not found' is not a valid HTTPStatus", 'input': {}}
                raise HTTPException(status_code=412, detail=er)
            
            
    async def update_comment(self, comment_uid: UUID, comment_data: UpgradeCommentSchema, uow: IUnitOfWork, owner_uid: UUID) -> OutputCommentSchema:
        async with uow:
            try:
                new_comment = await uow.comment.edit_one(comment_uid, comment_data.model_dump(exclude_none=True), uid_user=owner_uid)
                await uow.commit()
            except NoResultFound:
                er = {'type': 'value_error', 'loc': (), 'msg': "Value error, 'Comments not found' is not a valid HTTPStatus", 'input': {}}
                raise HTTPException(status_code=412, detail=er)
        return new_comment
    
    
comment_service = CommentService()