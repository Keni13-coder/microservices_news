from typing import Any, List

from .user_schemas import (
    OutputUserSchema,
    UserCreate,
    ChangeUserPassword,
    EmailSchema, 
    BaseModel
)

from .token_schemas import (
    OutputToken,
    LoginToken,
    PayloadToken,
    PayloadRefresh,
    TokenResponse
)

from .my_type_dict import (
    MessageDict,
    RefreshDict,
    AccessDict
)

from .services_second_schemas import (
    OutputPostModel as PostModel,
    RequestPostModel
)

class PathInfo(BaseModel):
    is_cache: bool


class Default(BaseModel):
    detail: dict[str, Any]
    info_api: dict[str, PathInfo]
    
class DefaultMessageOutput(Default):
    detail: dict[str, str]
    

class OutputUserModel(Default):
    detail: dict[str, OutputUserSchema]
    
class OutpuTokenResponse(TokenResponse):
    info_api: dict[str, PathInfo]
    
class OutputPostModel(Default):
    detail: dict[str, List[PostModel]]