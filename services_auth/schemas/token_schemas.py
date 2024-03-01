from datetime import datetime
from typing import Literal, Union
from uuid import UUID
from pydantic import UUID4, BaseModel, Field, model_validator


class RefreshToken(BaseModel):
    jti: UUID4 = Field(..., alias='refresh_token')
    user_uid: UUID4
    
    class Config:
        populate_by_name = True
        from_attributes=True
    
class OutputToken(RefreshToken):
    is_active: bool
    device_id: UUID4
    

class LoginToken(BaseModel):
    access_token: str
    refresh_token: str
    expire_refresh: datetime
    

class Payload(BaseModel):
    exp: int
    nbf: int


class PayloadToken(Payload):
    user_uid: Union[UUID4, str] = Field(..., alias='sub')
    device_id: Union[UUID4, str]
    
    @model_validator(mode='after')
    def str_in_uuid(self):     
        if isinstance(self.user_uid, str):
            self.user_uid = UUID(self.user_uid)      
        if isinstance(self.device_id, str):
            self.device_id = UUID(self.device_id)
            
        return self
    
    class Config:
        populate_by_name = True
    

class PayloadRefresh(Payload):
    token: OutputToken
    
    
class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal['bearer'] = 'bearer'