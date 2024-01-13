import io
import os
import shutil


import pytest
from httpx import AsyncClient
from fastapi import UploadFile as pack_image

from db.utils.uow_class import IUnitOfWork

from services.user_service import user_service
from apps.authapp.schemas import UserCreate, OutputUserSchema
from core.config import settings

@pytest.fixture(autouse=True, scope='session')
async def create_user(get_uow):
    data = UserCreate(**{'username':'test_post','email':'test_post@mail.ru','password':'test13'})
    token = await user_service.register_user(data=data, uow=get_uow)

 
@pytest.fixture(scope='session')
async def current_test_user(get_uow: IUnitOfWork):
    async with get_uow:
        user = await get_uow.user.find_one(username='test_post')
    assert user
    
    yield user

# file

@pytest.fixture(scope='session')
def get_file():
    path = './tests/post_services_test/fake_images/Warface_sample.jpg'
    with open(path, 'rb') as f:
        file = io.BytesIO(f.read())
    image = pack_image(
        file=file,
        filename='Warface_sample.jpg'
    )

    yield image


@pytest.fixture(scope='session')
def get_update_file():
    path = './tests/post_services_test/fake_images/NewCapture001.png'
    with open(path, 'rb') as f:
        file = io.BytesIO(f.read())
    image = pack_image(
        file=file,
        filename='NewCapture001.png'
    )

    yield image


@pytest.fixture(autouse=True ,scope='session')
def setup_media():
    os.mkdir(settings.MEDIA_URL)
    yield
    shutil.rmtree(settings.MEDIA_URL)



