from fastapi import HTTPException, Request
from core.config import TemplateResponse
from apps import titles

async def no_access(request: Request, exc: HTTPException):
    return TemplateResponse('error_pages/page_403.jinja2', context={'request': request, 'title': titles['page_403']})
