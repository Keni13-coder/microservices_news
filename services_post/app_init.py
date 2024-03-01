from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache import FastAPICache
from py_fastapi_logging.middlewares.logging import LoggingMiddleware

from api import router_post
from utils.broker import broker
from utils.data_redis import redis_manager
from core.config import settings
from utils import setup_header_tags


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with broker.lifespan_context(app):
        redis_manager
        FastAPICache.init(RedisBackend(redis_manager.redis), prefix="fastapi-cache")
        yield
        await broker.broker.close()


def create_app(debug=False):

    app = FastAPI(debug=debug, lifespan=lifespan)
    app.include_router(router_post, prefix=settings.PREFIX_API_VERSION, tags=['Post'], dependencies=[Depends(setup_header_tags)])
    # ПО работает в обратном порядке от зарешистрирования.
    # app.add_middleware(LoggingMiddleware, app_name='my_blog')

    return app