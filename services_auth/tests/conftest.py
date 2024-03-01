import asyncio

from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend


from core.config import settings
from run import app
from utils.broker import rabbit_broker, get_manager
from utils.data_redis import redis_manager
from utils.uow.uow_class import UnitOfWork
from background_celery.app_celery import celery


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
async def lifespan():
    async with rabbit_broker.lifespan_context(app):
        redis_manager
        FastAPICache.init(RedisBackend(redis_manager.redis), prefix="fastapi-cache")
        yield
        await rabbit_broker.broker.close()


@pytest.fixture(scope='session')
async def get_broker_manager():
    yield get_manager()
    
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


    
@pytest.fixture(scope="session")
def celery_worker_parameters():
    return {"perform_ping_check": False}