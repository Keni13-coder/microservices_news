from datetime import datetime, timedelta
import random
import string
import json
import time
from typing import Annotated
import hashlib

from uuid import UUID
from fastapi import Depends, HTTPException, Request, responses
from sqlalchemy.exc import NoResultFound
from authlib.jose import JsonWebSignature
from celery.result import AsyncResult

from apps.authapp.models import User, Token
from db.utils.uow_class import IUnitOfWork, UnitOfWork
from apps.authapp.schemas import ChangeUserPassword, OutputUserSchema, UserCreate, UserLoginSchema, OutputToken
from core.config import settings
from background_celery import send_message



UOWDep = Annotated[IUnitOfWork, Depends(UnitOfWork)]

class HashePasswordWorker:
    async def __get_random_string(self, lenght: int=12) -> str:
        '''Generates a random string used as a salt'''
        rnd_string = ''.join(random.choice(string.ascii_letters) for _ in range(lenght))
        return rnd_string

    # Хеширует пароль
    async def __hash_password(self, password: str, salt: str = None) -> str:
        '''Hashed the password'''
        if salt is None:
            salt = await self.__get_random_string()
        enc = hashlib.pbkdf2_hmac(hash_name='sha256', password=password.encode(), salt=salt.encode(), iterations=100_000)
        return enc.hex()

    async def _cerate_hashed_password(self, password: str) -> str:
        '''Creates a string of salt and hash'''
        salt = await self.__get_random_string()
        hashed_password = await self.__hash_password(password=password, salt=salt)
        return f'{salt}${hashed_password}'
    

    async def _validate_password(self, password: str, hashed_password: str) -> bool:
        '''Checks that the password hash matches the hash from the database'''
        salt, hashed = hashed_password.split('$')
        return await self.__hash_password(password=password, salt=salt) == hashed
        

    async def _change_password(self, new_password: str) -> str:
        new_password = await self._cerate_hashed_password(new_password)
        return new_password



class TokenWorker:
    async def _create_user_token(self, user_uid: UUID , uow: IUnitOfWork) -> UUID:
        '''Сreates a token and enters it into the database'''
        token_data = {'user_uid': user_uid}
        token_data['expires'] = datetime.utcnow() + timedelta(weeks=2)
        async with uow:
            token: Token = await uow.token.add_one(token_data)  
            
            await uow.commit()
        return token.token
    
    
    async def _get_token(self, token: UUID, uow: IUnitOfWork) -> OutputToken:
        async with uow:            
            try:
                token: Token = await uow.token.find_one(token=token)
            except NoResultFound:
                er = [{'type': 'value_error', 'loc': (), 'msg': "Value error, 'Token not found' is not a valid HTTPStatus", 'input': {}}]
                raise HTTPException(status_code=412, detail=er)
            return token


    async def _valid_expires_token(self, token: UUID, uow: IUnitOfWork) -> bool:
            token = await self._get_token(token, uow)
            if token:
                # return token.expires > datetime.utcnow()
                return token.expires > datetime.utcnow()
            return False
     
        
    async def _delete_token(self, token: UUID, uow: IUnitOfWork) -> UUID:
        async with uow:
            try:
                token_uid = await uow.token.deactivate_one(token)
            except NoResultFound:
                er = [{'type': 'value_error', 'loc': (), 'msg': "Value error, 'there is no such token' is not a valid HTTPStatus", 'input': {}}]
                raise HTTPException(status_code=412, detail=er)
            await uow.commit()
        return token_uid
    
    
    async def _redefinition_token(self, token: UUID, uow: IUnitOfWork) -> UUID|bool:
        valid_token = await self._valid_expires_token(token, uow)
        if valid_token:
            return token
        # возможна ошибка из-за того что valid вернет False если запись не будет найдена, сможет ли delete удалить записи который нет
        await self._delete_token(token, uow)
        return False
    
    
    @staticmethod    
    async def get_reset_token(uid: UUID, expires_sec=1800) -> str:
        '''token generation'''
        # алгоритм шифрования
        jws = JsonWebSignature(['HS256'])
        # переменная с словарём указывающим какой альгоритм был выбран
        protected = {'alg': 'HS256'}
        # делаем json строку из dict и переводим в байты с encode('utf-8')
        # время действия токена, время отправки полей, идентификатор пользователя.
        payload = json.dumps({
            'expires_sec':expires_sec,
            'time_sending':time.time(),
            'user_uid': str(uid)
        }).encode('utf-8')
        
        secret = settings.SECRET_KEY
        # return b''.decode = return str
        # Выполняем сериализацию токена на базе указанного алгоритма, набора данных с полезной нагрузкой, секретного ключа.
        return jws.serialize_compact(protected=protected, payload=payload, key=secret).decode('utf-8')
    
    
    @staticmethod
    async def get_payload_from_reset_token(token: str) -> dict | bool:
        jws = JsonWebSignature(['HS256'])
        data = jws.deserialize_compact(token, settings.SECRET_KEY)
        payload_json = json.loads(data['payload'])
        # считаем: (создание + время действия - время на данный момент)
        time_left = payload_json['time_sending'] + payload_json['expires_sec'] - time.time()
        
        if time_left < 0:
            return False
        else:
            return payload_json

    
    
class UserService(HashePasswordWorker, TokenWorker):
    
    async def __call__(self, request: Request, uow: UOWDep) -> OutputUserSchema:
        curren_token = request.cookies.get('token_user')
        if curren_token:
            async with uow:
                user = await uow.user._get_user_by_token(token=curren_token)
            if await self._redefinition_token(token=curren_token, uow=uow):
                return user
        er = [{'type': 'value_error', 'loc': (), 'msg': "Value error, 'The token does not exist or is outdated' is not a valid HTTPStatus", 'input': {}}]
        raise HTTPException(status_code=403, detail=er)
    
    
    async def register_user(self, data: UserCreate, uow: IUnitOfWork) -> UUID:
        data.password= await self._cerate_hashed_password(data.password)
        data = data.model_dump(by_alias=True)
        async with uow:
            user: OutputUserSchema = await uow.user.add_one(data)
            await uow.commit()
            
        token_token = await self._create_user_token(user.uid, uow)    
        return token_token   

        
        
    async def login_user(self, data: UserLoginSchema, uow: IUnitOfWork) -> UUID:
        password = data.password
        user: User = await self.get_user(uow, email=data.email)
        valid_password = await self._validate_password(password=password, hashed_password=user.hashed_password)
        if not valid_password:
            er = [{'type': 'value_error', 'loc': (), 'msg': "Value error, 'Incorrect data was entered' is not a valid HTTPStatus", 'input': {}}]
            raise HTTPException(status_code=401, detail=er)
            
        token_token = await self._create_user_token(user.uid, uow)    
        return token_token
        
        
    async def logout_user(self, current_token: UUID, uow: IUnitOfWork) -> dict:   
        token_uid = await self._delete_token(current_token, uow)
        return {'message': 'successe', 'token_uid': token_uid, 'detail': ''}
    
    
    async def get_user(self, uow: IUnitOfWork, **filter_by) -> OutputUserSchema:
        async with uow:
            try:
                user = await uow.user.find_one(**filter_by)
            except NoResultFound:
                er = [{'type': 'value_error', 'loc': (), 'msg': "Value error, 'User not found' is not a valid HTTPStatus", 'input': {}}]
                raise HTTPException(status_code=412, detail=er)
            return user
        
    async def get_user_by_token(self, token: UUID, uow: IUnitOfWork) -> OutputUserSchema|dict:
        async with uow:
            try:
                user = await uow.user._get_user_by_token(token=token)
            except NoResultFound:
                return {}
                    
            return user
    
    
    async def change_password(self, user_uid: UUID, data: ChangeUserPassword, uow: IUnitOfWork) -> dict:
        password = data.password
        async with uow:
            hashed_password = await self._change_password(password)
            response = {'hashed_password': hashed_password}
            try:
                await uow.user.edit_one(user_uid, response)
            except NoResultFound:
                er = [{'type': 'value_error', 'loc': (), 'msg': "Value error, 'Incorrect data was entered' is not a valid HTTPStatus", 'input': {}}]
                raise HTTPException(status_code=401, detail=er)

            await uow.commit()
        return {'message': 'success'}
    

    async def send_message(self, url:str, user: OutputUserSchema) -> None:
        '''Sends an email to the user'''
        test: AsyncResult = send_message.delay(url, user)
        return responses.JSONResponse(status_code=200, content={'message': 'email has been sent'})
    
    
    

    



current_user = UserService()
user_service = UserService()
