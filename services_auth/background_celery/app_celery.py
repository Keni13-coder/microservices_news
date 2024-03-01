from celery import Celery

from core.config import settings

from celery.app.log import Logging

celery = Celery(
    'app_celery',
    broker=settings.RABBITMQ_URL,
    backend=settings.REDIS_URL,
    broker_connection_retry_on_startup=True, 
    )





class CeleryConfig:
    worker_max_memory_per_child = 12000
    task_serializer = "pickle"
    result_serializer = "pickle"
    event_serializer = "json"
    accept_content = ["application/json", "application/x-python-serialize"]
    result_accept_content = ["application/json", "application/x-python-serialize"]
    
celery.config_from_object(CeleryConfig)
	
