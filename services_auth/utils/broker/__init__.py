from typing import Annotated

from fastapi import Depends
from .rabbit_app.broker import rabbit_broker
from .rabbit_app.rabbit_manager import Manager, broker_manager, get_manager

RabbitManagerDep = Annotated[Manager, Depends(get_manager)]