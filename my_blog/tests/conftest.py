from typing import AsyncGenerator

import pytest
import asyncio
from httpx import AsyncClient
# from sqlalchemy.pool import NullPool
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from db.base_class import Base
from apps.authapp.models import Token, User
from apps.postapp.models import Post, View, Comment
from db.utils.uow_class import  UnitOfWork, IUnitOfWork
from db.session import engine
from core.config import settings
from tests.async_database import create_database, database_exists
from run import app
import background_celery
from background_celery.app_celery import celery





@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    assert settings.MODE == 'TEST'

    if not await database_exists(settings.DB_URL):
        await create_database(settings.DB_URL)
            
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) 
    
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    

@pytest.fixture(scope='session')
def event_loop(request):
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()
    


@pytest.fixture(scope='session')
def get_uow():
    UOWDep = UnitOfWork()
    yield UOWDep




@pytest.fixture(scope='session')
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac


@pytest.fixture(autouse=True, scope='session')
async def startup():
    redis = aioredis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
    # для проверки подлючения
    redis_host = '127.0.0.1'
    await redis.ping()
    FastAPICache.init(RedisBackend(redis), prefix="test-fastapi-cache")
    
    
    


@pytest.fixture(scope='session')
def celery_app():
    celery.conf.update(CELERY_ALWAYS_EAGER=True)  # need it
    yield celery
    

@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': settings.RABBITMQ_URL,
        'result_backend': settings.REDIS_URL, # 'rpc://'
    }
    
    
@pytest.fixture(scope='session')
def celery_includes():
    return [
        'background_celery.post_tasks',
    ]
    
@pytest.fixture(scope='session')
def celery_parameters():
    return {
        'task_cls':  background_celery.post_tasks.TestCelery,
        'strict_typing': False,
    }

    
@pytest.fixture(scope="session")
def celery_worker_parameters():
    return {"perform_ping_check": False}
