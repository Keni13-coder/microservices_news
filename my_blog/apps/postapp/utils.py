import json

from fastapi.requests import Request


async def json_parse(request: Request):
    data = await request.body()
    return json.loads(data)