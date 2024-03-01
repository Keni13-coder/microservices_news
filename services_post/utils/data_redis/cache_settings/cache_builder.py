from typing import Optional
from urllib.parse import urlparse


from fastapi import Request, Response
from fastapi_cache import FastAPICache



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