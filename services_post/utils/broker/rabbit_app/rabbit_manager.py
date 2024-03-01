from abc import ABC, abstractmethod
from typing import Annotated, Type, AsyncGenerator
from fastapi import Depends

from utils.broker.rabbit_app.broker import broker
from utils.broker.rabbit_app.user_exch.sender import PostToUserSender
from utils.data_redis import redis_manager



class Manager(ABC):
    user_sender: Type[PostToUserSender]

    @abstractmethod
    def __init__(self):
        ...

    @abstractmethod
    async def __aenter__(self):
        ...
    
    @abstractmethod
    async def __aexit__(self, *args):
        ...


class RabbitManager(Manager):
    
    def __init__(self):
        self.broker = broker
        self.redis_manager = redis_manager
        
    async def __aenter__(self):
        self.user_sender = PostToUserSender(broker=self.broker, redis_manager=self.redis_manager)
 
        
    async def __aexit__(self, exc_type, exc, tb):
        ...
        
broker_manager = Annotated[Manager, Depends(RabbitManager)]

async def get_manager(manager: broker_manager) -> AsyncGenerator[Manager, None]:
    async with manager:
        yield manager