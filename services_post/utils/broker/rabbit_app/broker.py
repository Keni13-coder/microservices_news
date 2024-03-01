import asyncio
from contextlib import asynccontextmanager

from aiormq import AMQPConnectionError
from fastapi import FastAPI
from faststream.rabbit.fastapi import RabbitRouter

from core.config import settings
from utils.broker.rabbit_app.context import context
from utils.broker.rabbit_app.rabbit_logger import LoggerMiddleware, logger






@asynccontextmanager
async def lifespan(app: FastAPI):
    context.set_global("settings", settings)
    pingcounter = 0
    isconnect = False
    while not isconnect or pingcounter < 15:
        try:
            await broker.broker.connect(settings.RABBITMQ_URL)
            isconnect = True
            logger.info('CONNECTED TO THE BROKER')
            break
        except (AMQPConnectionError, ConnectionRefusedError):
            isconnect = False
            pingcounter += 1
            await asyncio.sleep(2)
            logger.info('WAIT CONNECT TO BROKER!!!')
            
            
    yield
    
    context.reset_global('settings')
    await broker.broker.close()

broker = RabbitRouter(schema_url="/asyncapi", include_in_schema=True, middlewares=[LoggerMiddleware], logger=logger, lifespan=lifespan)