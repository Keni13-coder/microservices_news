from .token_routes import token_router
from .user_routes import user_router


user_router.include_router(token_router)