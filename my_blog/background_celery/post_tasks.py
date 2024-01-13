import os
import typing

from celery import Task

from core.config import settings
from background_celery.image_to_json import image_deserialization
from background_celery.app_celery import celery



class TestCelery(Task):
    
    def __get_path_photo(self, image_filename: str, user_name: str):
        user_name = user_name.lower()
        image_filename = image_filename.replace(' ', '')
        finish_path = f'{user_name}/{image_filename}'
        return finish_path
    
    def __create_user_media_dir(self, full_path_to_media: str, file_name: str):
        if not os.path.exists(full_path_to_media):
            os.makedirs(full_path_to_media)
        open_file = full_path_to_media / file_name
        return open_file
            
            
    def __validaton_file_photo(self, path_photo: str) -> bool:
        path_photo = settings.MEDIA_URL / path_photo
        if os.path.exists(path_photo):
            return True
        return False
        

    def load_photo(self, data_image: dict, user_name: str) -> str:
        filename = data_image['filename'].replace(' ', '')
        user_name = user_name.lower()
        content =  data_image['image']
        full_path_to_media = settings.MEDIA_URL / user_name

        end_path = self.__create_user_media_dir(full_path_to_media, filename)

        with open(end_path, 'wb') as file:
            file.write(content)
            
        path = self.__get_path_photo(filename, user_name)
        return path



    def updatе_photo(self, data_image: dict, user_name: str) -> typing.Union[str, None]:
        filename = data_image['filename']
        path_photo = self.__get_path_photo(filename, user_name)
        valid = self.__validaton_file_photo(path_photo)
        if not  valid:
            path_photo = self.load_photo(data_image, user_name)
            
        return path_photo



@celery.task(bind=True, base=TestCelery)
def load_photo(self, data_image: dict, user_name: str):
    image = data_image['image']
    data_image['image'] = image_deserialization(image)
    path = self.load_photo(data_image, user_name)
    return path

@celery.task(bind=True, base=TestCelery)
def update_photo(self, data_image: dict, user_name: str):
    image = data_image['image']
    data_image['image'] = image_deserialization(image)
    path = self.updatе_photo(data_image, user_name)
    return path