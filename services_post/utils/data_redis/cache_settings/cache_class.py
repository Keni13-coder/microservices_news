import json
from typing import Any, List, Union
from fastapi_cache.coder import Coder, JsonEncoder, object_hook


from schemas import OutputPostSchemas


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
    def decode(cls, value: str) -> Union[List[OutputPostSchemas], OutputPostSchemas]:
        SCHEMAS_DATA = {
            'OutputPostSchemas': OutputPostSchemas,
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