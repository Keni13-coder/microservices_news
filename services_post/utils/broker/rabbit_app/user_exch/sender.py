from uuid import UUID, uuid4
from abc import ABC, abstractmethod
from fastapi import HTTPException
from fastapi_cache.decorator import cache
from faststream.rabbit.fastapi import RabbitRouter

from utils.broker.rabbit_app.user_exch.queues import exch
from schemas import ResponseSchemaGetUser
from utils.data_redis import cache_key_builder, RedisABC

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


class PostToUserSender(Sender):
    def __init__(self, broker: RabbitRouter, redis_manager: RedisABC):
        self.broker = broker
        self._operation_uid = ''
        self.redis_manager = redis_manager


    @cache(expire=60, key_builder=cache_key_builder)
    async def send_get(self, token: UUID) -> None:
        cur_uid = self._operation_uid = str(uuid4())
        await self.broker.broker.publish(
            token,
            exchange=exch,
            queue='get_user',
            content_type='application/json',
            correlation_id=cur_uid
            )
        return self

    async def get_resul(self, timeout: float=0.1):
        try:
            response = await self.redis_manager.get_data(key=self._operation_uid, execution_model=ResponseSchemaGetUser, timeout=timeout)

        except AssertionError as er:
            raise HTTPException(status_code=500, detail=str(er))
        
        return response
    
    
