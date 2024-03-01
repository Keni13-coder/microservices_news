from fastapi import UploadFile
from . import load_photo, update_photo
from .image_to_json import image_serialization


class WorkerPhotoCelery:
    @staticmethod
    async def load_photo_celery(image: UploadFile, username: str):
        image = await image_serialization(image)
        image_path = load_photo.delay(image, username).get(timeout=10)

        return image_path
    
    @staticmethod
    async def update_photo_celery(image: UploadFile, username: str):
        image = await image_serialization(image)
        image_path = update_photo.delay(image, username).get(timeout=10)
        return image_path
    
    
worker_photo_celery = WorkerPhotoCelery