from abc import ABC, abstractmethod
from typing import Annotated, AsyncGenerator, Type
from fastapi import Depends, HTTPException

from utils.broker.rabbit_app.broker import rabbit_broker
from utils.broker.rabbit_app.user_exch.sender import UserSender
from utils.data_redis import redis_manager


class Manager(ABC):
    user_sender: Type[UserSender]

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
        self.broker = rabbit_broker
        self.redis_manager = redis_manager

    async def __aenter__(self):
        self.user_sender = UserSender(broker=self.broker, redis_manager=self.redis_manager)
        
        
    async def __aexit__(self, exc_type, exc, tb):
        ...
        
        
broker_manager = Annotated[Manager, Depends(RabbitManager)]

async def get_manager(manager: broker_manager) -> AsyncGenerator[Manager, None]:
    async with manager:
        yield manager