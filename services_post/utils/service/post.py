from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound

from schemas import CreatePostClass, UpgradePostClass, OutputPostSchemas, CreateImage
from utils.uow.uow_class import IUnitOfWork
from utils.service.workers import PhotoWorker
    
from background_celery.class_worker_post import worker_photo_celery

from utils.dependences import UOWDep


class PostService(PhotoWorker):
    async def create_post(self, post_data: CreatePostClass, image_data: CreateImage, username: str, uow: IUnitOfWork, owner_uuid: UUID) -> OutputPostSchemas:
        image = await worker_photo_celery.load_photo_celery(image=image_data.image, username=username)
        post_data: dict = post_data.to_dict()
        post_data.update({'image': image, 'owner_uid': owner_uuid})

        async with uow:
            post: OutputPostSchemas = await uow.post.add_one(post_data)
            await uow.commit()
            
        return post


    async def get_post_all(self, uow: IUnitOfWork, limit: int, offset: int, **filter_by) -> List[OutputPostSchemas]:
        async with uow:
            try:
                posts: List[OutputPostSchemas] = await uow.post.find_all(limit=limit, offset=offset, **filter_by)
                
            except NoResultFound:
                er = {'type': 'value_error', 'loc': ('get_post_all', ), 'msg': "the post was not found according to the specified parameters", 'input': {**filter_by}}
                raise HTTPException(status_code=404, detail=er)
            
        return posts


    async def get_post_one(self, post_uid: UUID, uow: IUnitOfWork) -> OutputPostSchemas:
        async with uow:
            try:
                post: OutputPostSchemas = await uow.post.find_one(uid=post_uid)
            
            except NoResultFound:
                er = {'type': 'value_error', 'loc': ('get_post_one'), 'msg': "Value error, 'Post not found' is not a valid HTTPStatus", 'input': {'post_uid': post_uid}}
                raise HTTPException(status_code=404, detail=er)
            
        return post
    
    
    async def update_post(self, post_uid: UUID, update_data: UpgradePostClass, uow: IUnitOfWork, username: str, uid_user: UUID, image_data: CreateImage,) -> None:
        image = image_data.image
        update_data: dict = update_data.to_dict()

        if image:
            path = await worker_photo_celery.update_photo_celery(image=image, username=username)
            update_data.update({'image': path})

        async with uow:
            try:
                await uow.post.edit_one(post_uid, update_data, uid_user)
            
            except NoResultFound as ex:
                er = {'type': 'value_error', 'loc': ('update_post'), 'msg': "Value error, 'Post not found' is not a valid HTTPStatus", 'input':
                    {
                        'post_uid': post_uid,
                        'uid_user': uid_user
                        }
                    }
                raise HTTPException(status_code=404, detail=er)
            await uow.commit()
            
        return
    
    
    async def delete_post(self, post_uid, uow: IUnitOfWork, uid_user: UUID) -> None:
        async with uow:
            try:
                await uow.post.deactivate_one(post_uid, uid_user)
                
            except NoResultFound:
                er = {'type': 'value_error', 'loc': ('delete_post'), 'msg': "Value error, 'Post not found' is not a valid HTTPStatus", 'input': {post_uid}}
                raise HTTPException(status_code=404, detail=er)
            
            await uow.commit()
        return
        
    
    async def recent_publications(self, uow: UOWDep, limit: int):
        async with uow:
            res = await uow.post.recent(limit)
        
        return res
    
    async def popular_publications(self, uow: UOWDep, limit: int):
        async with uow:
            res = await uow.post.popular(limit)
            
        return res
    
    

post_service = PostService()

