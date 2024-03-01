from fastapi import APIRouter
from .comment_routes import router as router_comment
from .post_routes import router as router_post
from .view_routes import router as router_view

router_post.include_router(router_comment)
router_post.include_router(router_view)


