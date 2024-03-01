from datetime import timedelta
from uuid import UUID, uuid4

from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound

from schemas import ChangeUserPassword, LoginToken, OutputUserSchema, UserCreate, PayloadToken, MessageDict
from utils.security_classes import AuthProtocol
from utils.uow.uow_class import IUnitOfWork
from utils.service.workers import ABCHashePassword, ABCToken, token_worker, hashe_worker
from core.config import settings
from . import time_now
from background_celery import send_message


   
class UserService:
    def __init__(self, token_worker: ABCToken, hashe_worker: ABCHashePassword) -> None:
        self.token_worker = token_worker
        self.hashe_worker = hashe_worker
    

    async def create_user(self, data: UserCreate, uow: IUnitOfWork) -> None:
        data.password= await self.hashe_worker.create_hashed_password(data.password)
        data = data.model_dump(by_alias=True)
        async with uow:
            await uow.user.add_one(data)
            await uow.commit()
              
        return 
    
        
    async def login_user(self, data: AuthProtocol, uow: IUnitOfWork) -> LoginToken:
        password = data.password
        user: OutputUserSchema = await self.get_user(uow, email=data.email)
        valid_password = await self.hashe_worker.validate_password(password=password, hashed_password=user.hashed_password)
        if not valid_password:
            er = {'type': 'value_error', 'loc': (), 'msg': "Value error, 'Incorrect data was entered' is not a valid HTTPStatus", 'input': {}}
            raise HTTPException(status_code=401, detail=er)
        device_id = uuid4()
        access_token = await self.token_worker.create_access_token(user_uid=user.uid, device_id=device_id)
        expire_refresh = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE)
        now = time_now()
        refresh_token = await self.token_worker.create_refresh_token(
            user_uid=user.uid,
            jti=uuid4(),
            uow=uow,
            expire_minutes=expire_refresh,
            nbf=now,
            device_id=device_id
            )
        
        return LoginToken(access_token=access_token, refresh_token=refresh_token, expire_refresh=now + expire_refresh)
        
    
    async def logout_user(self, access_token: str, uow: IUnitOfWork) -> None:
        token: PayloadToken = await self.token_worker.get_access_token(token=access_token)
        await self.token_worker._delete_token(user_uid=token.user_uid, device_id=token.device_id, uow=uow)
        return
    
    
    async def get_user(self, uow: IUnitOfWork, **filter_by) -> OutputUserSchema:
        async with uow:
            try:
                user = await uow.user.find_one(**filter_by)
            except NoResultFound:
                er = {'type': 'value_error', 'loc': (), 'msg': "Value error, 'User not found' is not a valid HTTPStatus", 'input': {}}
                raise HTTPException(status_code=404, detail=er)
            return user
        
        
    async def get_user_by_token(self, token: str, uow: IUnitOfWork) -> OutputUserSchema:
        payload: PayloadToken = await self.token_worker.get_access_token(token)
        
        async with uow:
            try:
                user = await uow.user._get_user_by_token(user_uid=payload.user_uid, device_id=payload.device_id)
            except NoResultFound:
                er = {'type': 'value_error', 'loc': (), 'msg': "Value error, 'The user with this token was not found' is not a valid HTTPStatus", 'input': {}}
                raise HTTPException(status_code=404, detail=er)
                    
            return user

    
    
    async def change_password(self, user_uid: UUID, data: ChangeUserPassword, uow: IUnitOfWork) -> MessageDict:
        password = data.password
        async with uow:
            hashed_password = await self.hashe_worker.change_password(password)
            response = {'hashed_password': hashed_password}
            try:
                await uow.user.edit_one(user_uid, response)
            except NoResultFound:
                er = {'type': 'value_error', 'loc': (), 'msg': "Value error, 'User not found' is not a valid HTTPStatus", 'input': {}}
                raise HTTPException(status_code=401, detail=er)

            await uow.commit()
        return {'message': 'the password has been changed'}
    

    async def send_message(self, url: str, user: OutputUserSchema) -> MessageDict:
        '''Sends an email to the user'''
        send_message.delay(url, user)
        return {'message': 'email has been sent'}
    
    
    

    


user_service = UserService(token_worker=token_worker, hashe_worker=hashe_worker)
