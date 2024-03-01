from abc import ABC
from datetime import datetime
from typing import Any, Optional, Union, List
from enum import Enum

from pydantic import BaseModel, UUID4, EmailStr
from schemas.post_schemas import OutputPostSchemas


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

class ResponseSchemaGetPost(ABCSchemaGet):
    details: Union[List[OutputPostSchemas], ErrorPost]


class RequestSchamaGetPost(BaseModel):
    owner_uid: UUID4
    limit: int
    offset: int


 
   



class ResponseUserModel(BaseModel):
    uid: UUID4
    create_date: datetime
    email: EmailStr
    username: str
    hashed_password: str
    is_active: bool

    class Config:
        from_attributes=True
        
    def __repr__(self):
        return 'OutputUserSchema'
    
    def __str__(self):
        return 'OutputUserSchema'

  
class ResponseSchemaGetUser(ABCSchemaGet):
    details: Union[ResponseUserModel, ErrorPost]