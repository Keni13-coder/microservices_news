from abc import ABC, abstractmethod
import json
from uuid import uuid4

from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException
from faststream.rabbit.fastapi import RabbitRouter
from fastapi_cache.decorator import cache

from utils.broker.rabbit_app.user_exch.queues import exch
from schemas.services_second_schemas import ResponseSchemaGetPost, RequestPostModel
from utils.data_redis import RedisABC, cache_key_builder

class Sender(ABC):
    
    @abstractmethod
    def __init__(self):
        ...
    
    @abstractmethod    
    async def send_get(self, *args, **kwargs):
        ...
        
    @abstractmethod
    async def get_resul(self, timeout: float):
        ...



class UserSender(Sender):
    
    def __init__(self, broker: RabbitRouter, redis_manager: RedisABC):
        self.broker = broker
        self._operation_uid = ''
        self.redis_manager = redis_manager

    @cache(expire=60, key_builder=cache_key_builder)
    async def send_get(self, data: RequestPostModel) -> None:
        cur_uid = self._operation_uid = str(uuid4())
        await self.broker.broker.publish(
            data,
            exchange=exch,
            queue='all_posts_users',
            content_type='application/json',
            correlation_id=cur_uid
            )
        return self


    async def get_resul(self, timeout: float=0.1):
        try:
            response = await self.redis_manager.get_data(key=self._operation_uid, execution_model=ResponseSchemaGetPost, timeout=timeout)
        except AssertionError as ex:
            print(str(ex))
            raise HTTPException(status_code=500, detail=str(ex))
        
        return response

    
    
    