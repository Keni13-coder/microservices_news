from datetime import datetime

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, UUID4, Field, validator


class BasePassword(BaseModel):
    password: str = Field(..., title= 'password', pattern="[A-Za-z0-9@#$%^&+=]{4,}", min_length=4, max_length=100, alias='hashed_password')
    class Config:
        # позволяет пользоваться псовдонимом указанным в alias (точнее тоб программа считала что имя = псевдоним)
        populate_by_name = True
        from_attributes=True


class UserCreate(BasePassword):
    '''Checks the sign-up request'''
    username: str = Field(..., title= 'Name', min_length=4, max_length=100)
    email: EmailStr
    
    
class ChangeUserPassword(BasePassword):
    confirm_password: str = Field(..., title= 'password', pattern="[A-Za-z0-9@#$%^&+=]{4,}", min_length=4, max_length=100)
    
    @validator('confirm_password')
    def check_passwords_match(cls, v, values):
        if 'password1' in values and v != values['password']:
            er = [{'type': 'value_error', 'loc': (), 'msg': "Value error, 'passwords do not match' is not a valid HTTPStatus", 'input': {}}]
            raise HTTPException(status_code=412, detail=er)
        return v
    


class EmailSchema(BaseModel):
    email: EmailStr
      
class UserBase(BaseModel):
    '''Forms the response body with user details'''
    uid: UUID4
    create_date: datetime
    

class OutputUserSchema(UserBase):
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
 
    
    

