import json
from typing import Any, List, Union

from fastapi_cache.coder import Coder, JsonEncoder, object_hook

from schemas import OutputUserSchema


class CostumCoder(Coder):
    @classmethod
    def encode(cls, value: Any) -> str:
        response_value = value 
        if isinstance(value, list):
            response_value = []
            for obj in value:
                obj = obj.model_dump()
                response_value.append(obj)
        else:
            response_value = value.model_dump()
        
        value = response_value
        return json.dumps(value, cls=JsonEncoder)

    @classmethod
    def decode(cls, value: str) -> Union[List[OutputUserSchema], OutputUserSchema]:     
        decode = json.loads(value, object_hook=object_hook)

        if not isinstance(decode, list):
            response = OutputUserSchema(**decode)     

        else:
            response = []
            for post in decode:
                response.append(OutputUserSchema(**post))
                
        return response