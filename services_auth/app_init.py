from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from py_fastapi_logging.middlewares.logging import LoggingMiddleware
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache import FastAPICache

from api.routers.user_routes import user_router
from core.config import settings
from utils import setup_header_tags
from utils.broker import rabbit_broker
from utils.data_redis import redis_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with rabbit_broker.lifespan_context(app):
        redis_manager
        FastAPICache.init(RedisBackend(redis_manager.redis), prefix="fastapi-cache")
        yield
        await rabbit_broker.broker.close()


def create_app(debug=False):

    app = FastAPI(debug=debug, lifespan=lifespan)
    app.include_router(user_router, prefix=settings.PREFIX_API_VERSION, tags=['User'], dependencies=[Depends(setup_header_tags)])
    # app.add_middleware(LoggingMiddleware, app_name='my_blog')
    
    return app