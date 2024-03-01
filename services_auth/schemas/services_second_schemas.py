from datetime import date, datetime
from typing import Any, List, Optional, Union
from enum import Enum

from pydantic import UUID4, BaseModel
from schemas import OutputUserSchema

class Status(Enum):
    success = 'success'
    error = 'error'

class ErrorPost(BaseModel):
    type: str
    loc: tuple
    msg: str
    input : dict

    


class ABCSchemaGet(BaseModel):
    status: Status
    status_code: int = 200
    details: Union[Any, ErrorPost]


    
class ResponseSchemaGetUser(ABCSchemaGet):
    details: Union[OutputUserSchema, ErrorPost]
    
     
    
class _OutputCommentModel(BaseModel):
    uid: Optional[UUID4]
    create_date: Optional[datetime]
    content: Optional[str]
    post_uid: Optional[UUID4]
    owner_uid: Optional[UUID4]



class _OutputViewModel(BaseModel):
    uid: Optional[UUID4]
    post_uid: Optional[UUID4] 
    owner_uid: Optional[UUID4]


class OutputPostModel(BaseModel):
    uid: UUID4  
    owner_uid: UUID4
    create_date: Union[datetime, date]
    image: str
    title: str
    content: str
    is_active: bool
    comment: Optional[List[_OutputCommentModel]] = []
    view: Optional[List[_OutputViewModel]] = []
    class Config:
        from_attributes=True


class RequestPostModel(BaseModel):
    owner_uid: UUID4
    limit: int
    offset: int


    
class ResponseSchemaGetPost(ABCSchemaGet):
    details: Union[List[OutputPostModel], ErrorPost]