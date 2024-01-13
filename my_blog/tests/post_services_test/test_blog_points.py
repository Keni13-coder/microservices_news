from httpx import AsyncClient
import pytest
from celery.contrib.testing.worker import TestWorkController

from tests.conftest import IUnitOfWork



@pytest.fixture(scope='module')
async def login_user(ac: AsyncClient):
    data = {
        'email':'test_post@mail.ru',
        'password':'test13'
        }

    response = await ac.post('/login/', data=data)
    cookie = response.cookies.get('token_user')
    # assert response.status_code == 303
    # assert cookie


@pytest.mark.usefixtures('login_user')
class TestEndPointBlog:
    
    current_post = {'post_uid': None}
    
    async def test_add_post(self, ac: AsyncClient, celery_worker: TestWorkController):
        path = './tests/post_services_test/fake_images/Warface_sample.jpg'
        
        data = {
            'content': 'TEST_PYTEST_POINT',
            'title': 'PYTEST_POINT'
        }
        files = {'image': open(path, 'rb')}
        response = await ac.post('/blog/add_post/', data=data, files=files)
        
        assert response.status_code == 303
        
    
    async def test_show_post(self, ac: AsyncClient, get_uow: IUnitOfWork):
        async with get_uow:
            posts = await get_uow.post.find_all()
        assert posts
        post = posts[0]
        response = await ac.get(f'/blog/single/{post.uid}')
        cookie = response.cookies.get('post_uid')
        
        assert response.status_code == 200
        assert cookie
        
        self.current_post['post_uid'] = cookie
        
    async def test_edit_post(self, ac: AsyncClient, get_uow: IUnitOfWork, celery_worker: TestWorkController):
        path = './tests/post_services_test/fake_images/NewCapture001.png'
        
        data = {
            'content': 'TEST_PYTEST_POINT_EDIT',
            'title': 'PYTEST_POINT_EDIT'
        }
        files = {'image': open(path, 'rb')}
        post_uuid = self.current_post['post_uid']
        
        response = await ac.post(f'/blog/edit/{post_uuid}', data=data, files=files)
        
        assert response.status_code == 303
        
        
    async def test_remove_post(self, ac: AsyncClient):
        post_uuid = self.current_post['post_uid']
        response = await ac.get(f'/blog/remove/{post_uuid}')
        
        assert response.status_code == 303