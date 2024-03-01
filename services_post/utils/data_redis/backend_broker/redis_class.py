from abc import ABC, abstractmethod, abstractproperty
import asyncio
from typing import Annotated, Union

from redis.typing import ExpiryT, AbsExpiryT
import pydantic
from redis import asyncio as aioredis

from core.config import settings
from schemas import ABCSchemaGet, Status

from utils.data_redis.backend_broker import Singleton, redis_encode, redis_decode


class SettingSet(pydantic.BaseModel):
    ex: Union[ExpiryT, None] = 12
    px: Union[ExpiryT, None] = None
    nx: bool = False
    xx: bool = False
    keepttl: bool = False
    get: bool = False
    exat: Union[AbsExpiryT, None] = None
    pxat: Union[AbsExpiryT, None] = None


class RedisABC(ABC):
    
    @abstractmethod
    def __init__(self):
        raise NotImplementedError
    
    @abstractproperty
    def redis(self):
        raise NotImplementedError
    
    @abstractmethod
    def on_setup_redis(self, *args, **kwargs):
        raise NotImplementedError
    
    @abstractmethod
    async def set_data(self, *args, **kwargs):
        raise NotImplementedError
    
    @abstractmethod
    async def get_data(self, *args, **kwargs):
        raise NotImplementedError
    
    @abstractmethod
    async def get_keys(self, *args, **kwargs):
        raise NotImplementedError



class RedisManeger(RedisABC, Singleton):
    
    def __init__(self):
        self._redis = self.on_setup_redis()

    
    @property
    def redis(self):
        return self._redis
    
    
    def on_setup_redis(self):
        redis = aioredis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
        return redis
        
        
    async def set_data(self, data: pydantic.BaseModel, key: str, params: SettingSet = SettingSet()):
        encode_data = await redis_encode(data)
        await self._redis.set(name=key, value=encode_data, **params.model_dump())
        return

    async def get_data(self, key: str, execution_model: pydantic.BaseModel, timeout: float=0.1):
        await asyncio.sleep(timeout)

        response = await self._redis.get(name=key)
        
        assert response, f"'type': 'redis_error', 'loc': (), 'msg': 'An unknown error occurred on the server side'"
        
        resul: ABCSchemaGet = await redis_decode(encode_str=response, execution_model=execution_model)
        
        assert resul.status == Status.success, (f'message: {resul.details.model_dump()}\n' f'status_code: {resul.status_code}')
        
        return resul.details

    
    async def get_keys(self):
        keys = await self._redis.keys()
        return keys


redis_manager = RedisManeger()