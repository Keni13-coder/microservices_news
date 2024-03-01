from typing import List

from fastapi import APIRouter
from fastapi.requests import Request
from fastapi_cache.decorator import cache

from schemas import(
    UserCreate,
    EmailSchema,
    ChangeUserPassword,
    OutputUserSchema,
    DefaultMessageOutput,
    MessageDict,
    PayloadToken,
    RequestPostModel,
    OutputPostModel
    )
from core.config import settings
from utils.service.user import user_service
from utils.dependences import UOWDep, HateoasDEP, token
from utils.broker import RabbitManagerDep
from utils.broker.rabbit_app.user_exch.sender import UserSender
from utils.data_redis import cache_key_builder


user_router = APIRouter()

@user_router.get('/', response_model=DefaultMessageOutput)
@cache(expire=30, key_builder=cache_key_builder)
async def get_info_api(info_api: HateoasDEP):
    response = DefaultMessageOutput(
        detail={'note': f'available routes via api {settings.PREFIX_API_VERSION}'},
        info_api=info_api
        )
    return response


@user_router.post('/add-user/', response_model=DefaultMessageOutput)
async def add_user(user: UserCreate, uow: UOWDep, info_api: HateoasDEP):
    
    await user_service.create_user(user, uow)

    return {'detail': {'message': 'The creation was successful'}, 'info_api': info_api}
    

@user_router.post('/reset-password/', response_model=DefaultMessageOutput)
async def reset_password(request: Request, email: EmailSchema, uow: UOWDep, info_api: HateoasDEP):
             
    user: OutputUserSchema = await user_service.get_user(uow, email=email.email)
    token = await user_service.token_worker.reset_password_token(user_uid=user.uid)
    response: MessageDict = await user_service.send_message(url=request.url_for('change_password', token=token), user=user) # type: ignore
    
    return {'detail': response, 'info_api': info_api}
        

@user_router.patch('/change-password/{token}', response_model=DefaultMessageOutput)
async def change_password(token: str, password_math: ChangeUserPassword, uow: UOWDep, info_api: HateoasDEP):
    
    user_uid = await user_service.token_worker.get_payload_from_reset_token(token=token)
    response: MessageDict = await user_service.change_password(user_uid, password_math, uow)
    
    return {'detail': response, 'info_api': info_api}

@user_router.get('/posts/' ) #, response_model=OutputPostModel
@cache(expire=30, key_builder=cache_key_builder)
async def get_user_posts(access_token: token, broker_manager: RabbitManagerDep, info_api: HateoasDEP, limit: int = 1000, offset: int = 0):
    payload: PayloadToken = await user_service.token_worker.get_access_token(access_token)
    data = RequestPostModel(owner_uid=payload.user_uid, limit=limit, offset=offset)

    result: UserSender = await broker_manager.user_sender.send_get(data=data)
    responses = await result.get_resul()
    
    return {'detail': {'response_object': responses}, 'info_api': info_api}