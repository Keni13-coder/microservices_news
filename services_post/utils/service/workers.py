'''
Данный воркер нужен если celery отключить от проекта
'''

import os

from fastapi import UploadFile
from aiofile import async_open

from core.config import settings



class PhotoWorker:
    
    async def __create_user_media_dir(self, full_path_to_media: str, file_name: str):
        if not os.path.exists(full_path_to_media):
            os.makedirs(full_path_to_media)
        open_file = full_path_to_media / file_name
        return open_file
            

    async def __get_path_photo(self, image_filename: str, user_name: str):
        finish_path = f'{user_name}/{image_filename}'
        return finish_path


    async def __validaton_file_photo(self, path_photo: str) -> bool:
        if os.path.exists(path_photo):
            return True
        return False
        
    
    async def _load_photo(self, image: UploadFile, user_name: str) -> str:
        filename= image.filename.replace(' ', '')
        user_name = user_name.lower()
        content = await image.read()
        full_path_to_media = settings.MEDIA_URL / user_name
        open_file = await self.__create_user_media_dir(full_path_to_media, filename)
        
        async with async_open(open_file, 'wb') as file:
            await file.write(content) 
        path = await self.__get_path_photo(filename, user_name)
        
        return path
        
    
    
    async def _updatе_photo(self, new_image: UploadFile, user_name: str) -> str|None:
        filename = new_image.filename
        path_photo = await self.__get_path_photo(filename, user_name)
        if not await self.__validaton_file_photo(path_photo):
            await self._load_photo(new_image, user_name)
            return path_photo
        
        return None
        
        
    
    

    