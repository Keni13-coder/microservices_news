from typing import Annotated, Any, MutableMapping, Union
from faststream import context
from faststream.broker.fastapi.context import Context, Logger
from faststream.rabbit.fastapi import RabbitMessage

TimeoutType = Union[int, float, None]
   
CorrelationId = Annotated[str, Context('message.correlation_id')]