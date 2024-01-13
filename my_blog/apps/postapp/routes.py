from fastapi import APIRouter, HTTPException
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from pydantic_core._pydantic_core import ValidationError
from fastapi_cache.decorator import cache

from apps import titles
from core.config import TemplateResponse
from apps.dependencies import post_service, current_user, UOWDep, user_service, comment_service, recent, popular
from apps.postapp.schemas import CreatePost, CreateCommentSchema,  OutputUserSchema, UpgradePostSchema
from apps.postapp.utils import json_parse


post_router = APIRouter(prefix='/blog')



@post_router.get('/')
async def all_post(request: Request, uow: UOWDep, recent: recent, popular: popular):
    request.name = 'blog'
    context = {'request': request, 'recent': recent, 'popular': popular, 'title': titles['blog']}
    context['posts'] = await post_service.get_post_all(uow)
    token = request.cookies.get('token_user')
    context['user'] = await user_service.get_user_by_token(token, uow)

    return TemplateResponse('blog/blog.jinja2', context=context)


@post_router.get('/add_post/')
@post_router.post('/add_post/')
async def create_post(request: Request, current_user: current_user, uow: UOWDep, recent: recent, popular: popular):
    request.name = 'add_post'
    context = {'request': request, 'user': current_user, 'recent': recent, 'popular': popular, 'title': titles['create_post']}
    if request.method == 'POST':
        data = await request.form()
        try:
            post_data = CreatePost(**data, owner_uid=current_user.uid)
            new_post = await post_service.create_post(post_data, current_user.username, uow)
        except ValidationError as ex:
            context['errors'] = ex.errors()
            return TemplateResponse('blog/create_post.jinja2', context=context, status_code=400)

        except HTTPException as ex:
            context['errors'] = ex.detail
            return TemplateResponse('blog/create_post.jinja2', context=context, status_code=400)
        
        return RedirectResponse('/blog/', status_code=303)

    return TemplateResponse('blog/create_post.jinja2', context=context)


@post_router.get('/single/{uuid}')
async def show_post(uuid: str, request: Request, uow: UOWDep, recent: recent, popular: popular):
    context = {'request': request, 'recent': recent, 'popular': popular, 'title': titles['single-post']}
    token = request.cookies.get('token_user')
    user: OutputUserSchema = await user_service.get_user_by_token(token, uow)
    context['user'] = user
    owner_uid = user.uid if user else None
    post_full = await post_service.get_post_one(uuid, uow, owner_uid=owner_uid)

    context['post'] = post_full

    response = TemplateResponse('blog/single-post.jinja2', context=context)
    response.set_cookie('post_uid', uuid)
    return response


@post_router.get('/edit/{uuid}')
@post_router.post('/edit/{uuid}')
async def edit_post(uuid: str, request: Request, uow: UOWDep, current_user: current_user, recent: recent, popular: popular):
    user: OutputUserSchema = current_user
    post_full: dict = await post_service.get_post_one(uuid, uow, user.uid)

    context = {'request': request, 'post': post_full, 'user': user, 'recent': recent, 'popular': popular, 'title': titles['edit-post']}
    
    if request.method == 'POST':
        form = await request.form()
        try:
            valid_form = UpgradePostSchema(**form)

        except ValidationError as ex:
            context['errors'] = [er['msg'] for er in ex.errors()]
            
            return TemplateResponse('blog/edit-post.jinja2', context=context, status_code=400)
        
        except HTTPException as er:
            detail = er.detail[0]
            context['errors'] = [detail['msg']]
            
            return TemplateResponse('blog/edit-post.jinja2', context=context, status_code=er.status_code)
        
        try:
            await post_service.update_post(post_uid=uuid, update_data=valid_form, uow=uow, username=user.username)
        
        except HTTPException as er:
            detail = er.detail[0]
            context['errors'] = [detail['msg']]
            
            return TemplateResponse('blog/edit-post.jinja2', context=context, status_code=er.status_code)

        
        context['success'] = True
        return RedirectResponse('/blog/', status_code=303)
        
    return TemplateResponse('blog/edit-post.jinja2', context=context)


@post_router.get('/remove/{uuid}')
async def remove_post(uuid: str, request: Request, uow: UOWDep, current_user: current_user):
    await post_service.delete_post(uuid, uow)
    return RedirectResponse('/blog/', status_code=303)
    

@post_router.post('/add_comment')
async def add_comment(request: Request, uow: UOWDep, current_user: current_user):
    data = await json_parse(request=request)

    text = data.get('text')
    post_uid = data.get('postUid')
    user = current_user

    try:
        comment = CreateCommentSchema(content=text, post_uid=post_uid, owner_uid=user.uid)
        
    except ValidationError as ex:
        raise HTTPException(status_code=400, detail=ex.errors())

    comment = await comment_service.add_comment(comment, uow)
    
    
    return {'username': user.username, 'text': text}
