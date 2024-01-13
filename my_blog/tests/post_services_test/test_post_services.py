from contextlib import nullcontext as does_not_raise
import os
from typing import List, Union

from sqlalchemy.exc import NoResultFound
from fastapi import HTTPException, UploadFile
import pytest

from apps.postapp.schemas import CreatePost, OutputPostSchemas, UpgradePostSchema
from services.post_service import post_service
from tests.post_services_test.conftest import IUnitOfWork, OutputUserSchema, settings

from celery.contrib.testing.worker import TestWorkController


class TestPostService:
    ADD_POST = None
    ERRORS_ADD_POST = None
    
    current_post = {'post_uid': None}
    

    async def test_create_post(self, get_file: UploadFile, current_test_user: OutputUserSchema, get_uow: IUnitOfWork, celery_worker: TestWorkController):

        data = CreatePost(
            image=get_file,
            content='TEST_PYTEST',
            title='PYTEST',
            owner_uid=current_test_user.uid
        )
        post: OutputPostSchemas = await post_service.create_post(post_data=data, username=current_test_user.username, uow=get_uow)
        
        is_image = os.path.exists(settings.MEDIA_URL / post.image)
        
        assert post
        assert is_image
    
        self.current_post['post_uid'] = post.uid
    
    
    async def test_get_post_all(self, get_uow: IUnitOfWork):
        posts = await post_service.get_post_all(uow=get_uow)
        assert posts
        assert len(posts) == 1
        
        
    async def test_get_post_one(self, get_uow: IUnitOfWork, current_test_user: OutputUserSchema):
        post_uid = self.current_post['post_uid']
        post: OutputPostSchemas = await post_service.get_post_one(post_uid=post_uid, uow=get_uow)
        async with get_uow:
            view = await get_uow.view.find_all(post_uid=post_uid)
        assert post and len(view) == 0
        
        post: OutputPostSchemas = await post_service.get_post_one(post_uid=post_uid, uow=get_uow, owner_uid=current_test_user.uid)
        async with get_uow:
            view = await get_uow.view.find_all(post_uid=post_uid)
        
        assert post and len(view) == 1
        
        
    async def test_update_post(self, get_update_file: UploadFile, current_test_user: OutputUserSchema, get_uow: IUnitOfWork, celery_worker):
        update_data = UpgradePostSchema(
            image=get_update_file,
            content='NEW_TEST_PYTEST',
            title='NEW_PYTEST',
            owner_uid=current_test_user.uid
        )
        post_uid = self.current_post['post_uid']


        await post_service.update_post(post_uid=post_uid, update_data=update_data, username=current_test_user.username, uow=get_uow)
        
        async with get_uow:
            new_post: OutputPostSchemas = await get_uow.post.find_one(uid=post_uid)
            assert new_post
            new_path_image = new_post.image
            new_content = new_post.content == 'NEW_TEST_PYTEST'
            new_title = new_post.title == 'NEW_PYTEST'
            
            is_image = os.path.exists(settings.MEDIA_URL / new_path_image)

        assert is_image
        assert new_content
        assert new_title 
                  
   
    async def test_recent_publications(self, get_uow: IUnitOfWork):
        recent: List[OutputPostSchemas] = await post_service.recent_publications(uow=get_uow)
        post_uid = self.current_post['post_uid']
        assert recent
        assert len(recent) == 1
        assert recent[0].uid == post_uid
     
        
    async def test_popular_publications(self, get_uow: IUnitOfWork):
        popular: List[OutputPostSchemas] = await post_service.popular_publications(uow=get_uow)
        post_uid = self.current_post['post_uid']
        assert popular
        assert len(popular) == 1
        assert popular[0].uid == post_uid
    
    
    async def test_delete_post(self, get_uow: IUnitOfWork):
        post_uid = self.current_post['post_uid']
        async with get_uow:
            post: OutputPostSchemas = await get_uow.post.find_one(uid=post_uid)
            
        assert post.is_active
            
        await post_service.delete_post(post_uid=post_uid, uow=get_uow)
        
        with pytest.raises(NoResultFound, match='No row was found when one was required'):
            async with get_uow:
                deactivate_post: OutputPostSchemas = await get_uow.post.find_one(uid=post_uid)

    