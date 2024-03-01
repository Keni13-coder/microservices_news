from typing import Any, List, Union, Set
from pydantic import BaseModel


from .services_second_schemas import (
    ResponseUserModel,
    RequestSchamaGetPost,
    ResponseSchemaGetPost,
    ResponseSchemaGetUser,
    ABCSchemaGet,
    Status,
    )

from .post_schemas import (
    OutputPostSchemas,
    CreatePost,
    UpgradePost,
    CreateImage,
    UpgradeImage,
)

from .comment_schemas import (
    OutputCommentSchema, 
    CreateCommentSchema, 
    UpgradeCommentSchema,
)

from .view_schemas import (
    CreateViewSchema,
    OutputViewSchema
)

from .form_classes import (
    CreatePostClass,
    UpgradePostClass
)

class PathInfo(BaseModel):
    is_cache: bool


class Default(BaseModel):
    detail: dict[str, Any]
    info_api: dict[str, PathInfo]
    
class DefaultMessageOutput(Default):
    detail: dict[str, str]


class OutputViewModel(Default):
    detail: dict[str, List[OutputViewSchema]]


class OutputPostModel(Default):
    detail: dict[str, Union[OutputPostSchemas, List[OutputPostSchemas]]]


class OutputCommentModel(Default):
    detail: dict[str, List[OutputCommentSchema]]




