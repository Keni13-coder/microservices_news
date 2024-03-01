from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
import random
import string
import hashlib
from typing import Annotated, Optional, Union
from functools import wraps

from uuid import UUID, uuid4
from fastapi import Depends, HTTPException, status, Response
from sqlalchemy.exc import NoResultFound
from jose import jwt, JWTError

from utils.uow.uow_class import IUnitOfWork
from schemas import (
    OutputToken,
    PayloadToken,
    PayloadRefresh,
    RefreshDict,
    AccessDict
)
from core.config import settings
from utils.dependences import token, refresh_token_cookie, UOWDep
from . import time_now, uuid_in_str


class ABCHashePassword(ABC):
    @abstractmethod
    async def create_hashed_password(self, password: str):
        raise NotImplementedError

    @abstractmethod
    async def validate_password(self, password: str, hashed_password: str):
        raise NotImplementedError

    @abstractmethod
    async def change_password(self, new_password: str):
        raise NotImplementedError


class HashePasswordWorker(ABCHashePassword):
    async def __get_random_string(self, lenght: int = 12) -> str:
        '''Generates a random string used as a salt'''
        rnd_string = ''.join(random.choice(string.ascii_letters)
                             for _ in range(lenght))
        return rnd_string

    # Хеширует пароль
    async def __hash_password(self, password: str, salt: str = None) -> str:
        '''Hashed the password'''
        if salt is None:
            salt = await self.__get_random_string()
        enc = hashlib.pbkdf2_hmac(hash_name='sha256', password=password.encode(
        ), salt=salt.encode(), iterations=100_000)
        return enc.hex()

    async def create_hashed_password(self, password: str) -> str:
        '''Creates a string of salt and hash'''
        salt = await self.__get_random_string()
        hashed_password = await self.__hash_password(password=password, salt=salt)
        return f'{salt}${hashed_password}'

    async def validate_password(self, password: str, hashed_password: str) -> bool:
        '''Checks that the password hash matches the hash from the database'''
        salt, hashed = hashed_password.split('$')
        return await self.__hash_password(password=password, salt=salt) == hashed

    async def change_password(self, new_password: str) -> str:
        new_password = await self.create_hashed_password(new_password)
        return new_password


class ABCToken(ABC):
    @abstractmethod
    async def __call__(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def _create_token(self, data_encode: dict, expire_minutes: Optional[datetime] = None, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def _decode_token(self, token: str, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def create_access_token(self, user_uid: UUID, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def create_refresh_token(self, user_uid: UUID, jti: UUID, uow: IUnitOfWork, device_id: UUID, nbf: datetime, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def get_refresh_token(self, token: str, uow: IUnitOfWork, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def get_access_token(self, token: str, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def _permission_to_update(self, access_token: str, refresh_token: str, uow: IUnitOfWork, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def _delete_token(self, user_uid: UUID, device_id: UUID, uow: IUnitOfWork, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def _revoked_token(self, user_uid: UUID, device_id: UUID, uow: IUnitOfWork, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def reset_password_token(self, user_uid: UUID, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def get_payload_from_reset_token(self, token: str, *args, **kwargs):
        raise NotImplementedError


class TokenWorker(ABCToken):

    def refresh_decorator(funk):
        @wraps(funk)
        async def wrapper(
            self,
            access_token: str,
            refresh_token: str,
            uow: IUnitOfWork,
            response: Response,
            __exp: None,
        ):
            async def __time_to_delete(
                exp: datetime,
                user_uid: UUID,
                device_id: UUID,
                uow: IUnitOfWork,
                date_now: datetime,
                time_difference: timedelta = timedelta(
                    minutes=settings.ACCESS_TOREN_EXPIRE),
            ):
                if (_ := date_now + time_difference).timestamp() < exp:
                    ...
                else:
                    await self._delete_token(user_uid, device_id, uow)
                return

            data_new_tokens: PayloadToken = await self._permission_to_update(access_token=access_token, refresh_token=refresh_token, uow=uow)
            user_uid = data_new_tokens.user_uid
            device_id = data_new_tokens.device_id
            exp = data_new_tokens.exp
            nbf = data_new_tokens.nbf

            await self._revoked_token(user_uid, device_id, uow)
            await __time_to_delete(exp=exp, user_uid=user_uid, device_id=device_id, uow=uow, date_now=time_now())

            new_refresh_token = await self.create_refresh_token(
                user_uid=user_uid,
                jti=uuid4(),
                uow=uow,
                expire_minutes=exp,
                nbf=nbf,
                device_id=device_id
            )

            access_token = await self.create_access_token(user_uid=user_uid, device_id=device_id)

            token = await funk(self, uow, access_token, new_refresh_token, response, exp)

            return token

        return wrapper


    @refresh_decorator
    async def __call__(
        self,
        uow: UOWDep,
        access_token: token,
        refresh_token: refresh_token_cookie,
        response: Response,
        __exp: Optional[datetime] = None
    ) -> str:

        response.set_cookie(key='refresh_token', value=refresh_token,
                            expires=__exp, httponly=True, secure=True)

        return access_token


    async def _create_token(
        self,
        data_encode: dict,
        nbf: datetime,
        expire_minutes: Optional[timedelta] = None,
        exp: Optional[datetime] = None,
        algorithm: str = settings.ALGORITHM,
        secret_key: str = settings.SECRET_KEY,
    ) -> str:
        if not (expire_minutes or exp):
            raise ValueError(
                'pass one of the arguments "expire_minutes", "exp".')

        if not exp:
            exp = nbf + expire_minutes

        data_encode.update({'exp': exp, 'nbf': nbf})
        return jwt.encode(claims=data_encode, key=secret_key, algorithm=algorithm)


    async def _decode_token(
        self,
        token: str,
        expired=False,
        algorithm: str = settings.ALGORITHM,
        secret_key: str = settings.SECRET_KEY
    ) -> Union[RefreshDict, AccessDict]:
        
        payload = None
        exception = HTTPException(status_code=403, detail={
                                  'massage': 'The transmitted parameters have not been confirmed'})
        try:
            if expired:
                def is_expired_token(exp) -> bool:
                    now = datetime.now(timezone.utc).timestamp()
                    resul = exp < now
                    return resul

                payload = jwt.decode(token, secret_key, algorithm, options={
                                     'verify_exp': False})

                if not is_expired_token(payload['exp']):
                    raise exception

            else:
                payload = jwt.decode(token, secret_key, algorithm)

        except JWTError:
            raise exception

        return payload


    @uuid_in_str
    async def create_access_token(
        self,
        user_uid: UUID,
        device_id: UUID,
        expire_minutes: timedelta = timedelta(
            minutes=settings.ACCESS_TOREN_EXPIRE),
    ) -> str:
        '''Сreates access token'''
        token_data = {'sub': user_uid, 'device_id': device_id}

        access_token = await self._create_token(token_data, expire_minutes=expire_minutes, nbf=time_now())
        return access_token


    @uuid_in_str
    async def create_refresh_token(
        self,
        user_uid: UUID,
        jti: UUID,
        uow: IUnitOfWork,
        nbf: datetime,
        device_id: UUID,
        expire_minutes: timedelta = timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE),
    ) -> str:
        refresh_data = {'jti': jti}
        add_token = {'user_uid': user_uid, "device_id": device_id}
        add_token.update(refresh_data)

        async with uow:
            await uow.token.add_one(add_token)
            await uow.commit()

        return await self._create_token(refresh_data, expire_minutes=expire_minutes, nbf=nbf)


    async def __get_token(
        self,
        token: str,
        expired: bool = False
    ) -> Union[RefreshDict, AccessDict]:
        return await self._decode_token(token, expired=expired)


    async def get_refresh_token(self, token: str, uow: IUnitOfWork) -> PayloadRefresh:
        decode_payload = await self.__get_token(token)
        jti = decode_payload['jti']
        async with uow:
            try:
                token: OutputToken = await uow.token.find_one(jti=jti)
            except NoResultFound:
                er = {'type': 'value_error', 'loc': (
                ), 'msg': "Value error, 'Token not found' is not a valid HTTPStatus", 'input': {}}
                raise HTTPException(status_code=412, detail=er)

        assert token.is_active, await self._delete_token(token.user_uid, token.device_id, uow)

        return PayloadRefresh(token=token, exp=decode_payload['exp'], nbf=decode_payload['nbf'])


    async def get_access_token(self, token: str, expired: bool = False) -> PayloadToken:
        payload = await self.__get_token(token, expired=expired)
        return PayloadToken(**payload)


    async def _permission_to_update(self, access_token: str, refresh_token: str, uow: IUnitOfWork) -> PayloadToken:
        '''
        Checks the correspondence of access_token and refresh_token for user identification

        Note:
            defines the lifetime of refresh_token and expired access_token

        Returns:
            user_uid: uuid

        Errors:
            HTTPException

        '''
        access_payload = await self.get_access_token(access_token, expired=True)

        try:
            refresh_token_model: PayloadRefresh = await self.get_refresh_token(refresh_token, uow=uow)
        except AssertionError:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={
                                'error_message': 'Repeated attempt to access the resource'})
        try:
            assert refresh_token_model.token.user_uid == access_payload.user_uid and refresh_token_model.token.device_id == access_payload.device_id, 'Access denied'
        except AssertionError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={
                                'error_message': 'Data inconsistency detected - Access denied'})

        return PayloadToken(user_uid=access_payload.user_uid, device_id=access_payload.device_id, exp=refresh_token_model.exp, nbf=refresh_token_model.nbf)


    async def _delete_token(self, user_uid: UUID, device_id: UUID, uow: IUnitOfWork) -> str:
        async with uow:
            try:
                await uow.token.delete_all(user_uid=user_uid, device_id=device_id)
            except NoResultFound:
                er = {'type': 'value_error', 'loc': (
                ), 'msg': "Value error, 'there is no such token' is not a valid HTTPStatus", 'input': {}}
                raise HTTPException(status_code=412, detail=er)
            await uow.commit()
        return 'All user tokens have been deleted'


    async def _revoked_token(self, user_uid: UUID, device_id: UUID, uow: IUnitOfWork) -> None:
        async with uow:
            try:
                await uow.token.deactivate_all(user_uid=user_uid, device_id=device_id)
            except NoResultFound:
                er = {'type': 'value_error', 'loc': (
                ), 'msg': "Value error, 'there is no such token' is not a valid HTTPStatus", 'input': {}}
                raise HTTPException(status_code=412, detail=er)
            await uow.commit()
        return


    async def reset_password_token(
        self,
        user_uid: UUID,
        expires_minutes: float = 30.0,
        algorithm: str = settings.ALGORITHM,
        secret_key: str = settings.SECRET_KEY,
    ) -> str:

        data_encode = {'user_uid': str(user_uid)}

        return await self._create_token(
            data_encode=data_encode,
            expire_minutes=timedelta(minutes=expires_minutes),
            nbf=time_now(),
            algorithm=algorithm,
            secret_key=secret_key
        )


    async def get_payload_from_reset_token(self, token: str) -> str:
        try:
            payload = self.__get_token(token)
            return payload['user_uid']
        except JWTError as ex:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={
                                'error_message': ex})
        


token_worker = TokenWorker()
RefreshTokenDep = Annotated[str, Depends(token_worker)]
hashe_worker = HashePasswordWorker()
