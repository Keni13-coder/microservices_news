from datetime import datetime, date
from typing import List, Optional, Union

from pydantic import UUID4, BaseModel, validator, model_validator
from fastapi import HTTPException, UploadFile, File

from core.img_extension import img_extension
from apps.authapp.schemas import OutputUserSchema

        
class PostBase(BaseModel):
    image: UploadFile = File(...)
    class Config:
        from_attributes=True
    
    
    @validator('image', check_fields=True)
    def image_path(cls, value):
        file_name = value.filename.replace(' ', '')
        extension = file_name.split('.')[-1].lower()

        if value and not img_extension[extension]:
            er = [{'type': 'value_error', 'loc': ('image', ), 'msg': "Value error, 'available extension for images", 'input': {}, 'suitable_ext': [ext.value for ext in img_extension]}]
            raise HTTPException(detail=er, status_code=400)

        return value

        
class CreatePost(PostBase):
    title: str
    content: str
    owner_uid: UUID4
    
    
class UpgradePostSchema(PostBase):
    title: Optional[str] = None
    image: Optional[UploadFile] = File(default=None)
    content: Optional[str] = None

    @model_validator(mode='before')
    def valid_data(cls, values):
        image = values['image']
        values['image'] = image if image.filename else None
        valid_dict = {k:v for k, v in values.items() if v}
        if not valid_dict:
            er = [{'type': 'value_error', 'loc': (), 'msg': "Value error, 'At least 1 field must be filled in' is not a valid HTTPStatus", 'input': {}}]
            raise HTTPException(detail=er, status_code=400)
        return valid_dict


class CommentBase(BaseModel):
    content: str
    post_uid: UUID4
    owner_uid: UUID4
   
    class Config:
        from_attributes=True
        
        
class CreateCommentSchema(CommentBase):
    pass


class UpgradeCommentSchema(BaseModel):
    content: str
    

class OutputCommentSchema(CommentBase):
    uid: Optional[UUID4]
    create_date: Optional[datetime]
    content: Optional[str]
    post_uid: Optional[UUID4]
    owner_uid: Optional[UUID4]
    owner: Optional[OutputUserSchema] = None


class ViewBase(BaseModel):
    class Config:
        from_attributes=True
    
class CreateViewSchema(ViewBase):
    post_uid: UUID4
    owner_uid: UUID4


        
class OutputViewSchema(ViewBase):
    uid: Optional[UUID4]
    post_uid: Optional[UUID4] 
    owner_uid: Optional[UUID4]


class OutputPostSchemas(BaseModel):
    uid: UUID4  
    owner_uid: UUID4
    create_date: Union[datetime, date]
    image: str
    title: str
    content: str
    is_active: bool
    owner: Optional[OutputUserSchema] = None
    comment: Optional[List[OutputCommentSchema]] = []
    view: Optional[List[OutputViewSchema]] = []
    class Config:
        from_attributes=True
        # arbitrary_types_allowed = True
        
    def __repr__(self):
        return 'OutputPostSchemas'
    
    def __str__(self):
        return 'OutputPostSchemas'