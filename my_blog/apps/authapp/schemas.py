from typing import Optional, List
from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, UUID4, Field, validator
from datetime import datetime


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., title= 'password', pattern="[A-Za-z0-9@#$%^&+=]{4,}", min_length=4, max_length=100)


class UserCreate(BaseModel):
    '''Checks the sign-up request'''
    username: str = Field(..., title= 'Name', min_length=4, max_length=100)
    email: EmailStr
    password: str = Field(..., title= 'password', pattern="[A-Za-z0-9@#$%^&+=]{4,}", min_length=4, max_length=100, alias='hashed_password')
    
    class Config:
        # позволяет пользоваться псовдонимом указанным в alias (точнее тоб программа считала что имя = псевдоним)
        populate_by_name = True
        from_attributes=True
        
class UserBase(BaseModel):
    '''Forms the response body with user details'''
    uid: UUID4
    create_date: datetime
    

    
    
class OutputToken(BaseModel):
    uid: UUID4
    token: UUID4 = Field(..., alias='access_token')
    expires: datetime
    user_uid: UUID4

    class Config:
        populate_by_name = True
        from_attributes=True
        
    @validator('token')
    def hexlify_token(cls, value):
        ''' Converts UUID to hex string '''
        return value.hex
    
    
class CreateToken(BaseModel):
    user_uid: UUID4
    
# Поменял название с User
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


class EmailSchema(BaseModel):
    email: EmailStr
    
    
    
class ChangeUserPassword(BaseModel):
    password: str = Field(..., title= 'password', pattern="[A-Za-z0-9@#$%^&+=]{4,}", min_length=4, max_length=100)
    confirm_password: str = Field(..., title= 'password', pattern="[A-Za-z0-9@#$%^&+=]{4,}", min_length=4, max_length=100)
    
    @validator('confirm_password')
    def check_passwords_match(cls, v, values):
        if 'password1' in values and v != values['password']:
            er = [{'type': 'value_error', 'loc': (), 'msg': "Value error, 'passwords do not match' is not a valid HTTPStatus", 'input': {}}]
            raise HTTPException(status_code=412, detail=er)
        return v
    
    class Config:
        from_attributes=True