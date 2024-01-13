from contextlib import nullcontext as does_not_raise
from typing import Union

from httpx import AsyncClient
from uuid import UUID
import pytest
from fastapi import HTTPException

from apps.authapp.schemas import UserCreate, OutputToken, OutputUserSchema, UserLoginSchema
from tests.conftest import IUnitOfWork
from services.user_service import user_service, current_user



class TestUserService:
    '''
    Checks the main functions of the UserService class
    Note:
        don't forget to enable redis to make the tests run faster
    '''
    
    
    DATA_REGISTERS = ({'username':'test','email':'test@mail.ru','password':'test13'}, does_not_raise())
    
    DATA_REGISTER_ERRORS = [
        ({'username':'test','email':'test@mail.ru','password':'test13'}, pytest.raises(HTTPException)),
        ({'username':'test1','email':'test@mail.ru','password':'test13'}, pytest.raises(HTTPException)),
        ({'username':'test','email':'test12@mail.ru','password':'test13'}, pytest.raises(HTTPException))
    ]
    
    DATA_LOGIN = ({'email':'test@mail.ru','password':'test13'}, does_not_raise())
    
    DATA_LOGIN_ERRORS = [
        ({'email':'test12@mail.ru','password':'test13'}, pytest.raises(HTTPException)),
        ({'email':'test@mail.ru','password':'test131'}, pytest.raises(HTTPException)),
        ({'email':'test12@mail.ru','password':'test131'}, pytest.raises(HTTPException)),
    ]
    
    worker_token = {'token_user': None}
    
    
    @pytest.mark.parametrize(
        'data, expectation',
        [
            DATA_REGISTERS,
            *DATA_REGISTER_ERRORS
        ]
    )
    async def test_registor_user(self, data:dict, expectation: Union[None, HTTPException], get_uow: IUnitOfWork):
        with expectation:
            data = UserCreate(**data)
            token_token: UUID = await user_service.register_user(data=data, uow=get_uow)
            async with get_uow:
                users = await get_uow.user.find_all()
                tokens = await get_uow.token.find_all()
                token: OutputToken = await get_uow.token.find_one(token=token_token)
                user: OutputUserSchema = await get_uow.user.find_one(uid=token.user_uid)
                
            assert len(users) == 1
            assert len(tokens) == 1
            assert token.user_uid == user.uid
    
    
    
    @pytest.mark.parametrize(
        'data, expectation',
        [
            DATA_LOGIN,
            *DATA_LOGIN_ERRORS
        ]
    )
    async def test_login_user(self, data: dict, expectation: Union[None, HTTPException], get_uow: IUnitOfWork):
        with expectation:
            login = UserLoginSchema(**data)
            token_token: UUID = await user_service.login_user(data=login, uow=get_uow)
            async with get_uow:
                token: OutputToken = await get_uow.token.find_one(token=token_token)
                assert token
                user: OutputUserSchema = await get_uow.user.find_one(uid=token.user_uid)
    
            assert user
            token = self.worker_token['token_user'] = token_token

    
    async def test_get_user_by_token(self, get_uow: IUnitOfWork):
        response_token = self.worker_token.get('token_user')
        assert response_token
        user = await user_service.get_user_by_token(token=response_token, uow=get_uow)
        assert user
        

    async def test_current_user(self, ac: AsyncClient, get_uow: IUnitOfWork):
        with pytest.raises(HTTPException):
            await current_user(request=ac, uow=get_uow)
        




        

        
