
from uuid import UUID
from fastapi import APIRouter
from fastapi_cache.decorator import cache

from utils.service.post import post_service
from schemas import (
    ResponseUserModel,
    OutputPostModel,
    DefaultMessageOutput,
    )
from core.config import settings
from utils.broker import RabbitManagerDep, PostToUserSender
from utils.dependences import (
    UOWDep,
    image, 
    uprage_image,
    CreatePost,
    UpgradePost,
    token_cookie,
    HateoasDEP,
    )
from utils.data_redis import cache_key_builder

router = APIRouter()


@router.get('/', response_model=DefaultMessageOutput)
@cache(expire=30, key_builder=cache_key_builder)
async def get_info_api(info_api: HateoasDEP):
    response = DefaultMessageOutput(
        detail={'note': f'available routes via api {settings.PREFIX_API_VERSION}'},
        info_api=info_api
        )
    return response


@router.get('/posts-views-comments/', response_model=OutputPostModel) 
@cache(expire=30, key_builder=cache_key_builder)
async def all_post(uow: UOWDep, info_api: HateoasDEP, limit=1000, offset=0):
    posts = await post_service.get_post_all(uow, limit=limit, offset=offset)
    response = OutputPostModel(detail={'response_object': posts}, info_api=info_api)
    return response


@router.post('/add-post/', status_code=201, response_model=OutputPostModel)
async def create_post(uow: UOWDep, post_data: CreatePost, token_uid: token_cookie, image: image, info_api: HateoasDEP, bm: RabbitManagerDep):
    resul: PostToUserSender  = await bm.user_sender.send_get(token=token_uid)
    user: ResponseUserModel = await resul.get_resul(timeout=1.0)
    post = await post_service.create_post(post_data, image, user.username, uow, owner_uuid=user.uid)
    response = OutputPostModel(detail={'response_object': post}, info_api=info_api)
    return response


@router.get('/one-post/{uuid}/', response_model=OutputPostModel)
@cache(expire=30, key_builder=cache_key_builder)
async def show_post(uuid: str, uow: UOWDep, info_api: HateoasDEP):

    post = await post_service.get_post_one(uuid, uow)
    response = OutputPostModel(detail={'response_object': post}, info_api=info_api)
    return response


@router.put('/edit/{uuid}/', response_model=DefaultMessageOutput)
async def edit_post(uuid: str, uow: UOWDep, upgrade_form: UpgradePost, token_uid: token_cookie, uprage_image: uprage_image,  bm: RabbitManagerDep, info_api: HateoasDEP):

    resul: PostToUserSender = await bm.user_sender.send_get(token=token_uid)
    user: ResponseUserModel = await resul.get_resul(timeout=1.0)
        
    await post_service.update_post(post_uid=uuid, update_data=upgrade_form, uow=uow, username=user.username, image_data=uprage_image, uid_user=user.uid)

    response = DefaultMessageOutput(detail={'message': 'the post has been updated'}, info_api=info_api)
        
    return response
        

@router.delete('/remove/{uuid}/', response_model=DefaultMessageOutput)
async def remove_post(uuid: str, uow: UOWDep, token_uid: token_cookie, bm: RabbitManagerDep, info_api: HateoasDEP):
    resul: PostToUserSender = await bm.user_sender.send_get(token=token_uid)
    user: ResponseUserModel = await resul.get_resul(timeout=1.0)
        
    await post_service.delete_post(uuid, uow, user.uid)
    response = DefaultMessageOutput(detail={'message': 'the post has been deleted'}, info_api=info_api)
    return response
    

@router.get('/recent/', response_model=OutputPostModel)
@cache(expire=60, key_builder=cache_key_builder)
async def recent(uow: UOWDep, info_api: HateoasDEP, limit: int=5):
    posts_recent = await post_service.recent_publications(uow=uow, limit=limit)
    response = OutputPostModel(detail={'response_object': posts_recent}, info_api=info_api)
    return response


@router.get('/popular/', response_model=OutputPostModel)
@cache(expire=60, key_builder=cache_key_builder)
async def popular(uow: UOWDep, info_api: HateoasDEP, limit: int=5):
    posts_popular = await post_service.popular_publications(uow=uow, limit=limit)
    response = OutputPostModel(detail={'response_object': posts_popular}, info_api=info_api)
    return response
 
