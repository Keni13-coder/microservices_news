from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Request
from fastapi.responses import JSONResponse
from fastapi_cache.decorator import cache

from utils.service.view import view_service
from schemas import (
    CreateViewSchema,
    OutputViewModel,
    DefaultMessageOutput,
    ResponseUserModel
    )
from utils.dependences import UOWDep, token_cookie, HateoasDEP
from utils.broker import RabbitManagerDep, PostToUserSender
from utils.data_redis import cache_key_builder


router = APIRouter(prefix='/view', tags=['View'])


@router.post('/add-view/', response_model=DefaultMessageOutput)
async def add_view(view_data: CreateViewSchema, uow: UOWDep, token_uid: token_cookie, bm: RabbitManagerDep, info_api: HateoasDEP):

    resul: PostToUserSender  = await bm.user_sender.send_get(token=token_uid)
    user: ResponseUserModel = await resul.get_resul(timeout=1.0)
        
    await view_service.view_add(view_data=view_data, uow=uow, owner_uid=user.uid)
    
    response = DefaultMessageOutput(detail={'message': 'view created'}, info_api=info_api)
    return response
   
@router.get('/views-post-all/{post_uid}/', response_model=OutputViewModel)
@cache(expire=30, key_builder=cache_key_builder)
async def get_views_post(request: Request, post_uid: Annotated[UUID, Path()], uow: UOWDep, info_api: HateoasDEP):
    views = await view_service.get_view_all(post_uid=post_uid, uow=uow)
    response = OutputViewModel(detail={'response_object': views}, info_api=info_api)
    return response

