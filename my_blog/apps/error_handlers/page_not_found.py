from fastapi import HTTPException, Request
from core.config import TemplateResponse
from apps import titles

async def not_found(request: Request, exc: HTTPException):
    return TemplateResponse('error_pages/page_not_found.jinja2', context={'request': request, 'title': titles['page_not_found']})
