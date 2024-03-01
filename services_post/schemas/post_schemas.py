from datetime import datetime, date
from typing import List, Optional, Union

from pydantic import UUID4, BaseModel, validator, model_validator
from fastapi import HTTPException, UploadFile, File

from core.img_extension import img_extension
from schemas.comment_schemas import OutputCommentSchema
from schemas.view_schemas import OutputViewSchema


        
class ValidationPhoto(BaseModel):
    image: UploadFile = File(...)

    
    
    @validator('image', check_fields=True)
    def image_path(cls, value):
        file_name = value.filename.replace(' ', '')
        extension = file_name.split('.')[-1].lower()

        if value and not img_extension[extension]:
            er = {'type': 'value_error', 'loc': ('image', ), 'msg': "Value error, 'available extension for images", 'input': {}, 'suitable_ext': [ext.value for ext in img_extension]}
            raise HTTPException(detail=er, status_code=400)

        return value

    class Config:
        from_attributes=True



class CreateImage(ValidationPhoto):
    pass


class UpgradeImage(ValidationPhoto):
    image: UploadFile = File(default=None)

        
class CreatePost(BaseModel):
    title: str
    content: str


    
    
class UpgradePost(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None




class OutputPostSchemas(BaseModel):
    uid: UUID4  
    owner_uid: UUID4
    create_date: Union[datetime, date]
    image: str
    title: str
    content: str
    is_active: bool
    comment: Optional[List[OutputCommentSchema]] = []
    view: Optional[List[OutputViewSchema]] = []
    class Config:
        from_attributes=True

        
    def __repr__(self):
        return 'OutputPostSchemas'
    
    def __str__(self):
        return 'OutputPostSchemas'
    
    
    
    

    
    