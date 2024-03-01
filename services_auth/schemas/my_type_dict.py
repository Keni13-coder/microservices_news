from typing import TypedDict


class MessageDict(TypedDict):
    message: str
    
    
class TokenDict(TypedDict):
    device_id: str
    exp: int
    nbf: int
    
class RefreshDict(TokenDict):
    jti: str
    user_uid: str

    
class AccessDict(TokenDict):
    sub: str
