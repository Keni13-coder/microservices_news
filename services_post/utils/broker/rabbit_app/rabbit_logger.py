import logging
from logging.config import dictConfig
from typing import Optional

from faststream import BaseMiddleware
from faststream.types import DecodedMessage, SendableMessage


from utils.broker.rabbit_app.context import context


logger = logging.getLogger(name='rabbit-log')


class LoggerMiddleware(BaseMiddleware):
    async def on_receive(self):
        c = context.get_local("log_context")
        print(type(self.msg))
        logger.info(msg=f'Send to consumer -> {self.msg}', extra=c,)
        return await super().on_receive()
    
    
    async def on_publish(self, msg: SendableMessage) -> SendableMessage:
        c = context.get_local("log_context")
        logger.info(msg=f'Redirecting to consumer -> {msg}', extra=c)
        return await super().on_publish(msg)

    async def after_publish(self, err: Optional[Exception]) -> None:
        if err:
            c = context.get_local("log_context")
            logger.error(msg=err, extra=c)
        return await super().after_publish(err)
    
    async def on_consume(self, msg: DecodedMessage) -> DecodedMessage:
        c = context.get_local("log_context")
        logger.info(msg=f'Received -> {msg}', extra=c)
        return await super().on_consume(msg)

    async def after_consume(self, err: Optional[Exception]) -> None:
        if err:
            logger.error(msg=err)
        return await super().after_consume(err)
    
    
dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} {levelname} - {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose', 
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': './logs/faststeam.log',
            'formatter': 'json',  
        },
    },
    'loggers':{
        'rabbit-log':{
        'handlers': ['console', 'file'],
        'level': 'INFO',
        }
       
    }
})