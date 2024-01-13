from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from apps import titles
from apps.authapp.routes import user_router
from core.config import TemplateResponse, settings
from apps.postapp.routes import post_router
from apps.dependencies import UOWDep, user_service, recent, popular

api_router = APIRouter(tags=['Main'])
api_router.include_router(user_router, tags=['Auth'])
api_router.include_router(post_router, tags=['Post'])

@api_router.get('/', response_class=HTMLResponse)
@api_router.post('/', response_class=HTMLResponse)
async def root(request: Request, uow: UOWDep, recent: recent, popular: popular):
    request.name = 'home'
    token = request.cookies.get('token_user')
    user = await user_service.get_user_by_token(token=token, uow=uow)
    context = {'request': request, 'user': user, 'recent': recent, 'popular': popular, 'title': titles['index']}
    return TemplateResponse('index.jinja2', context=context)



@api_router.on_event("startup")
async def startup():
    redis = aioredis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

