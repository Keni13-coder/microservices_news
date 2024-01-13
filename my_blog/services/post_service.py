import os
from typing import List, Annotated

from fastapi import Depends
from fastapi import HTTPException, UploadFile
from uuid import UUID
from aiofile import async_open
from sqlalchemy.exc import NoResultFound, IntegrityError

from core.config import settings
from apps.postapp.schemas import CreateCommentSchema, CreatePost, UpgradeCommentSchema,\
    UpgradePostSchema, OutputCommentSchema, CreateViewSchema, OutputViewSchema, OutputPostSchemas
    
from db.utils.uow_class import IUnitOfWork

from services.user_service import UOWDep
from background_celery import  load_photo, update_photo
from background_celery.image_to_json import image_serialization

from celery.result import AsyncResult



class PhotoWorker:
    
    async def __create_user_media_dir(self, full_path_to_media: str, file_name: str):
        if not os.path.exists(full_path_to_media):
            os.makedirs(full_path_to_media)
        open_file = full_path_to_media / file_name
        return open_file
            

    async def __get_path_photo(self, image_filename: str, user_name: str):
        finish_path = f'{user_name}/{image_filename}'
        return finish_path


    async def __validaton_file_photo(self, path_photo: str) -> bool:
        if os.path.exists(path_photo):
            return True
        return False
        
    
    async def _load_photo(self, image: UploadFile, user_name: str) -> str:
        filename= image.filename.replace(' ', '')
        user_name = user_name.lower()
        content = await image.read()
        full_path_to_media = settings.MEDIA_URL / user_name
        open_file = await self.__create_user_media_dir(full_path_to_media, filename)
        
        async with async_open(open_file, 'wb') as file:
            await file.write(content) 
        path = await self.__get_path_photo(filename, user_name)
        
        return path
        
    
    
    async def _updatе_photo(self, new_image: UploadFile, user_name: str) -> str|None:
        filename = new_image.filename
        path_photo = await self.__get_path_photo(filename, user_name)
        if not await self.__validaton_file_photo(path_photo):
            await self._load_photo(new_image, user_name)
            return path_photo
        
        return None
        
        

class CommentService:

    async def add_comment(self, comment: CreateCommentSchema, uow: IUnitOfWork) -> OutputCommentSchema:
        async with uow:
            comment = await uow.comment.add_one(comment.model_dump())
            await uow.commit()
        return comment
    
    async def get_comment_all(self, post_uid: UUID, uow: IUnitOfWork) -> List[OutputCommentSchema]:
        async with uow:
            try:
                comments = await uow.comment.find_all(post_uid=post_uid)
            except NoResultFound:
                er = [{'type': 'value_error', 'loc': (), 'msg': "Value error, 'Comments not found' is not a valid HTTPStatus", 'input': {}}]
                raise HTTPException(status_code=412, detail=er)
            
        return comments
        
    async def count_comment(self, post_uid: UUID, uow: IUnitOfWork) -> int:
        comments = await self.get_comment_all(post_uid, uow)
        count = len(comments)
        return count
    
    async def delete_comment(self, comment_uid: UUID, uow: IUnitOfWork) -> None:
        async with uow:
            try:
                await uow.comment.deactivate_one(comment_uid)
                await uow.commit()
            except NoResultFound:
                er = [{'type': 'value_error', 'loc': (), 'msg': "Value error, 'Comments not found' is not a valid HTTPStatus", 'input': {}}]
                raise HTTPException(status_code=412, detail=er)
            
    async def delete_comment_all(self,  post_uid: UUID, uow: IUnitOfWork) -> None:
        # возможна ошибки завязынные на ретурне uid тк у нас будет список
        async with uow:
            try:
                await uow.comment.deactivate_all(post_uid)
                await uow.commit()
            except NoResultFound:
                er = [{'type': 'value_error', 'loc': (), 'msg': "Value error, 'Comments not found' is not a valid HTTPStatus", 'input': {}}]
                raise HTTPException(status_code=412, detail=er)
            
            
    async def update_comment(self, comment_uid: UUID, comment_data: UpgradeCommentSchema, uow: IUnitOfWork) -> OutputCommentSchema:
        async with uow:
            try:
                new_comment = await uow.comment.edit_one(comment_uid, comment_data.model_dump(exclude_none=True))
                await uow.commit()
            except NoResultFound:
                er = [{'type': 'value_error', 'loc': (), 'msg': "Value error, 'Comments not found' is not a valid HTTPStatus", 'input': {}}]
                raise HTTPException(status_code=412, detail=er)
        return new_comment
        
        


class VieWorker:
    async def __view_add(self, view_data: CreateViewSchema, uow: IUnitOfWork) -> None:
        data = view_data.model_dump()
        async with uow:
            try:
                await uow.view.add_one(data)
                await uow.commit()
                
            except IntegrityError:
                pass

    async def __get_view_all(self, post_uid: UUID, uow: IUnitOfWork) -> List[OutputViewSchema]:
        async with uow:
            try:
                views = await uow.view.find_all(post_uid=post_uid) 
            
            except NoResultFound:
                er = [{'type': 'value_error', 'loc': (), 'msg': "Value error, 'View not found' is not a valid HTTPStatus", 'input': {}}]
                raise HTTPException(status_code=412, detail=er)
            
        return views
    
    
    async def _counter_views(self, post_uid: UUID, uow: IUnitOfWork) -> int:
        count = await self.__get_view_all(post_uid, uow)
        return len(count)
    
    
    async def _manager_view(self, post_uid: UUID, uow: IUnitOfWork, owner_uid: UUID = None ) -> int:
        if owner_uid:
            view_data = CreateViewSchema(post_uid=post_uid, owner_uid=owner_uid)
            await self.__view_add(view_data, uow)
        count_post = await self._counter_views(post_uid, uow)
        return count_post
    
    


class PostService(VieWorker, PhotoWorker):
    async def create_post(self, post_data: CreatePost, username: str, uow: IUnitOfWork) -> OutputPostSchemas:
        image = post_data.image
        image: dict = image_serialization(image)
        post_data.image = load_photo.delay(image, username).get(timeout=10)
        async with uow:
            post: OutputPostSchemas = await uow.post.add_one(post_data.model_dump())
            await uow.commit()
        return post


    async def get_post_all(self, uow: IUnitOfWork) -> List[OutputPostSchemas]:
        async with uow:

            posts: List[OutputPostSchemas] = await uow.post.find_all()

        return posts

    async def get_post_one(self, post_uid: UUID, uow: IUnitOfWork, owner_uid: UUID = None) -> OutputPostSchemas:
        count_post = await self._manager_view(post_uid, uow, owner_uid)
        async with uow:
            try:
                post: OutputPostSchemas = await uow.post.find_one(uid=post_uid)
            
            except NoResultFound:
                er = [{'type': 'value_error', 'loc': (), 'msg': "Value error, 'Post not found' is not a valid HTTPStatus", 'input': {}}]
                raise HTTPException(status_code=412, detail=er)
            
        return post
    
    
    async def update_post(self, post_uid: UUID, update_data: UpgradePostSchema, uow: IUnitOfWork, username: UUID) -> None:
        image = update_data.image
        if image:
            image: dict = image_serialization(image)
            path = update_photo.delay(image, username).get(timeout=10)
            if path:
                update_data.image = path
                
        update_data = update_data.model_dump(exclude_unset=True, exclude_none=True, exclude_defaults=True)
        async with uow:
            try:
                await uow.post.edit_one(post_uid, update_data)
            
            except NoResultFound:
                er = [{'type': 'value_error', 'loc': (), 'msg': "Value error, 'Post not found' is not a valid HTTPStatus", 'input': {}}]
                raise HTTPException(status_code=412, detail=er)
            await uow.commit()
        return
    
    
    async def delete_post(self, post_uid, uow: IUnitOfWork):
        async with uow:
            await uow.post.deactivate_one(post_uid)
            await uow.commit()
        
    
    async def recent_publications(self, uow: UOWDep):
        async with uow:
            res = await uow.post.recent()
        
        return res
    
    async def popular_publications(self, uow: UOWDep):
        async with uow:
            res = await uow.post.popular()
            
        return res
    
    

post_service = PostService()
comment_service = CommentService()
recent = Annotated[List, Depends(post_service.recent_publications)]
popular = Annotated[List, Depends(post_service.popular_publications)]


