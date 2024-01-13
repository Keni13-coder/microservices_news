from typing import Any, List, Optional, Union
from urllib.parse import urlparse
import json

from fastapi import Request, Response
from fastapi_cache import FastAPICache
from fastapi_cache.coder import Coder, JsonEncoder, object_hook
from starlette.responses import JSONResponse

from apps.postapp.models import OutputPostSchemas
from apps.authapp.models import OutputUserSchema

def cache_key_builder(
    func,
    namespace: Optional[str] = "",
    request: Request = None,
    response: Response = None,
    *args,
    **kwargs
):
    prefix = FastAPICache.get_prefix()
    if request:
        parsed = urlparse(str(request.url))
        cache_key = f"{prefix}:{namespace}:{func.__module__}:{func.__name__}:{parsed.path}"
    else:
        cache_key = f"{prefix}:{namespace}:{func.__module__}:{func.__name__}:{args}:{kwargs}"
    return cache_key




class CostumCoder(Coder):
    @classmethod
    def encode(cls, value: Any) -> str:
        response_value = value 
        if isinstance(value, list):
            response_value = []
            for obj in value:
                schema_name = str(obj)
                obj = obj.model_dump()
                obj['schema'] = schema_name
                response_value.append(obj)
        else:
            schema_name = str(response_value)
            response_value = value.model_dump()
            response_value['schema'] = schema_name
        
        value = response_value
        return json.dumps(value, cls=JsonEncoder)

    @classmethod
    def decode(cls, value: str) -> Union[List[OutputPostSchemas], List[OutputUserSchema]]  | Union[OutputPostSchemas, OutputUserSchema]:
        SCHEMAS_DATA = {
            'OutputPostSchemas': OutputPostSchemas,
            'OutputUserSchema' : OutputUserSchema
        }
        
        decode = json.loads(value, object_hook=object_hook)

        if not isinstance(decode, list):
            type_schema = decode.pop('schema', '')
            schema = SCHEMAS_DATA.get(type_schema)
            response = schema(**decode)     

        else:
            response = []
            for post in decode:
                type_schema = post.pop('schema', '')
                schema = SCHEMAS_DATA.get(type_schema)
                response.append(schema(**post))
        return response