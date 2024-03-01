from datetime import datetime, timedelta, timezone
from uuid import UUID

def time_now(utc=True):
    date = datetime.now()
    if utc:
        date = datetime.now(timezone.utc)
        
    return date


def uuid_in_str(func):
    async def wrapper(self, *args, **kwargs):
        if args:
            args = [str(el) if isinstance(el, UUID) else el for el in args ]
        if kwargs:
            kwargs = {key: str(value) if isinstance(value, UUID) else value for key, value in kwargs.items()}
        return await func(self, *args, **kwargs)
    return wrapper