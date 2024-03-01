from abc import ABC, abstractmethod
from uuid import UUID

from aio_pika import ExchangeType
from fastapi import HTTPException
from faststream.rabbit import RabbitQueue, RabbitExchange #, RabbitRouter
from faststream.rabbit.asyncapi import Publisher

from utils.broker.rabbit_app.broker import rabbit_broker as user_router
from schemas.services_second_schemas import ResponseSchemaGetUser
from utils.broker.rabbit_app.context import CorrelationId, RabbitMessage
from utils.service.user import user_service
from utils.dependences import UOWDep
from utils.data_redis import redis_manager

exch = RabbitExchange("user-post", type=ExchangeType.DIRECT)


class QueueRabbit(ABC):
    publish_input_queue: RabbitQueue
    consumer_queue: RabbitQueue
    publisher: Publisher

    @abstractmethod
    async def on_message(*agrs, **kwargs):
        raise NotImplementedError
    
    
    


class ConcumerUserGet(QueueRabbit):
    consumer_queue = RabbitQueue('get_user')
    
    @user_router.subscriber(path=consumer_queue, exchange=exch)
    async def on_message(access_token: str, message: RabbitMessage, cur_id: CorrelationId, uow: UOWDep) -> ResponseSchemaGetUser:
        response = ResponseSchemaGetUser
        try:
            user = await user_service.get_user_by_token(uow=uow, token=access_token)
            response = response(status='success', details=user)
        except HTTPException as ex:
            response = response(status='error', details=ex.detail, status_code=ex.status_code)

        await redis_manager.set_data(data=response, key=cur_id)
        return response
