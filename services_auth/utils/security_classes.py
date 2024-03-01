from typing import Union, Protocol
from typing_extensions import Annotated
from fastapi.param_functions import Form
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import EmailStr
from core.config import settings
 
class UserLoginAuth2(OAuth2PasswordRequestForm):
    def __init__(
        self,
        *,
        grant_type: Annotated[Union[str, None], Form(pattern="password")] = None,
        username: Annotated[EmailStr, Form()],
        password: Annotated[str, Form(title= 'password', pattern="[A-Za-z0-9@#$%^&+=]{4,}", min_length=4, max_length=100)],
        scope: Annotated[str, Form()] = "",
        client_id: Annotated[Union[str, None], Form()] = None,
        client_secret: Annotated[Union[str, None], Form()] = None,
        ):
        self.grant_type = grant_type
        self.email = username
        self.password = password
        self.scope = scope
        self.client_id = client_id
        self.client_secret = client_secret
        
        
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.PREFIX_API_VERSION}/token/", scheme_name='auth')


class AuthProtocol(Protocol):
    grant_type: str | None = None
    email: EmailStr
    password: str
    scope: str = ""
    client_id: str | None = None
    client_secret: str | None = None
        
    
