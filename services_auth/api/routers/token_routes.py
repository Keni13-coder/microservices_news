from uuid import UUID
from fastapi import APIRouter, Request, Response

from schemas import DefaultMessageOutput, LoginToken, OutpuTokenResponse
from utils.dependences import HateoasDEP, UOWDep, form_data, token
from utils.service.user import user_service
from utils.service.workers import RefreshTokenDep


token_router = APIRouter(prefix='/token', tags=['Token'])


@token_router.post('/', response_model=OutpuTokenResponse)
async def login(data_login: form_data, uow: UOWDep, response: Response, info_api: HateoasDEP):  
    user_token: LoginToken = await user_service.login_user(data_login, uow)
    response.set_cookie(key='refresh_token', value=user_token.refresh_token, expires=user_token.expire_refresh, httponly=True, secure=True)
    
    return {'access_token': user_token.access_token, 'token_type': 'bearer', 'info_api': info_api}
    

@token_router.post('/refresh/', response_model=OutpuTokenResponse)
async def refresh_token(access_token: RefreshTokenDep, info_api: HateoasDEP):
    return {'access_token': access_token, 'token_type': 'bearer', 'info_api': info_api}


@token_router.delete('/del-token/', response_model=DefaultMessageOutput)
async def logout(access_token: token, uow: UOWDep, info_api: HateoasDEP):
    await user_service.logout_user(access_token=access_token, uow=uow)
    
    return {
        'detail':{'message': 'the token has been deleted'},
        'info_api': info_api
        }

