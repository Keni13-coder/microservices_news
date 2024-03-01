from typing import Annotated

from fastapi import Depends

from .rabbit_app.broker import broker
from .rabbit_app.rabbit_manager import broker_manager, RabbitManager, Manager, get_manager

from .rabbit_app.user_exch.sender import PostToUserSender

RabbitManagerDep = Annotated[Manager, Depends(get_manager)]