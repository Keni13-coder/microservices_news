import json
from fastapi import Request
from fastapi.routing import APIRoute
from core.config import settings



async def setup_header_tags(request: Request):
    scope = request.scope
    
    route = scope['route']
    tags = json.dumps(route.tags).encode()
    
    headers = scope['headers']
    headers.append((b'router-tags', tags))




async def hateoas_dict(request: Request):
    path = request.url.path
    is_main_path = True if path == f'{settings.PREFIX_API_VERSION}/' else False
    routes = request.app.routes
    try:
        tags = json.loads(request.headers.get('router-tags'))
        
    except TypeError:
        return
    
    response_dict = dict()
    for router in routes:
        if isinstance(router, APIRoute) and (is_main_path or tags == router.tags):
            method = tuple(router.methods)[0]

            response_dict.update(
                {
                    f'{method}{router.path}': {'is_cache' : True if 'GET' == method else False}   
                }
            )
    return response_dict
