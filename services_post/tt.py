from abc import ABC, abstractmethod
import asyncio
from enum import Enum
from functools import wraps
from typing import Annotated, Any, AsyncGenerator, Type
from uuid import UUID, uuid4
from fastapi import Depends, FastAPI, HTTPException
from functools import partial
from celery.result import AsyncResult


app = FastAPI()




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
    
    def __init__(self):
        self.data = {}
        self._operation_uid = ''
    
    async def send_get(self, messgae) -> None:
        cur_uid = self._operation_uid = str(uuid4())
        await asyncio.sleep(1.0)
        self.data[cur_uid] = messgae
        return self

    async def get_resul(self, timeout: float=0.1):
        response = self.data[self._operation_uid]
        return response
    

class ABCManager(ABC):
    post_sender: Type[Sender]
    
    @abstractmethod
    async def __aenter__(self):
        ...
    @abstractmethod
    async def __aexit__(self, exc_type, exc, tb):
        ...


class Manager(ABCManager):

    def __init__(self):
        self.broker = 'broker'
        
    
    async def __aenter__(self):
        self.post_sender = PostToUserSender()

       
    
    async def __aexit__(self, exc_type, exc, tb):
        ...
        

manager = Annotated[ABCManager, Depends(Manager)]

async def get_manager(manager: manager) -> AsyncGenerator[Manager, None]:
    async with manager:
        yield manager


ManagerDep = Annotated[Manager, Depends(get_manager)]

@app.get('/test-asyncio/')
async def geting(manager: ManagerDep):
    resul = await manager.post_sender.send_get('hello')
    return {'message': resul}


