from abc import ABC, abstractmethod
from uuid import UUID

from fastapi import HTTPException
from aio_pika import ExchangeType
from faststream.rabbit import RabbitQueue, RabbitExchange
from faststream.rabbit.asyncapi import Publisher

from utils.broker.rabbit_app.broker import broker as user_router
from schemas import  ResponseSchemaGetPost, RequestSchamaGetPost
from utils.broker.rabbit_app.context import CorrelationId, RabbitMessage
from utils.service.post import post_service
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
    


class ConsumerPostAll(QueueRabbit):
    consumer_queue = RabbitQueue('all_posts_users', durable=True)
    
    @user_router.subscriber(path=consumer_queue, exchange=exch)
    async def on_message(data: RequestSchamaGetPost, message: RabbitMessage, cur_id: CorrelationId, uow: UOWDep) -> ResponseSchemaGetPost:
        response = ResponseSchemaGetPost

        try:
            posts = await post_service.get_post_all(uow=uow, **data.model_dump())
            response = response(status='success', details=posts)
        except HTTPException as ex:
            response = response(status='error', details=ex.detail, status_code=ex.status_code)

        await redis_manager.set_data(data=response, key=cur_id)

        return response
    
