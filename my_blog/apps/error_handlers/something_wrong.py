from fastapi import HTTPException, Request
from core.config import TemplateResponse
from apps import titles

async def server_error(request: Request, exc: HTTPException):
    return TemplateResponse('error_pages/page_500.jinja2', context={'request': request, 'title': titles['page_500']})