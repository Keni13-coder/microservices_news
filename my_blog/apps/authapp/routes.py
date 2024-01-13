from fastapi import APIRouter, HTTPException, responses
from fastapi.requests import Request

from pydantic_core._pydantic_core import ValidationError

from apps.authapp.schemas import UserCreate, UserLoginSchema, EmailSchema, ChangeUserPassword
from core.config import TemplateResponse
from apps.dependencies import UOWDep, user_service, popular, recent
from apps import titles
from apps.authapp.models import  OutputUserSchema


user_router = APIRouter()

@user_router.post('/register/')
@user_router.get('/register/')
async def register(request: Request, uow: UOWDep, popular: popular, recent: recent):
    context = {'request': request, 'popular': popular, 'recent': recent, 'title': titles['register']}
    if request.method == 'POST':
        # проверить как происходит фалидация данных при регистрации
        form = await request.form()
        try:
            user = UserCreate(**form)

        except ValidationError as ex:
            context['errors'] = [error['msg'] for error in ex.errors()]
            return TemplateResponse('auth/register.jinja2', context=context, status_code=400)
        try:
            
            token_token: OutputUserSchema = await user_service.register_user(user, uow)
        except HTTPException as er:
            detail = er.detail[0]
            context['errors'] = [detail['msg']]
            return TemplateResponse('auth/register.jinja2', context=context, status_code=er.status_code)
        
        response = responses.RedirectResponse('/', status_code=303)
        response.set_cookie('token_user', token_token)
        return response
    
    request.name = 'register'
    return TemplateResponse('auth/register.jinja2', context)


@user_router.post('/login/')
@user_router.get('/login/')
async def login_page(request: Request, uow: UOWDep, popular: popular, recent: recent):
    context = {'request': request, 'popular': popular, 'recent': recent, 'title': titles['login']}
    
    
    if request.method == 'POST':
        form = await request.form()
        try:
            data = UserLoginSchema(**form)
            user_token = await user_service.login_user(data, uow)
            
        except ValidationError as ex:
            context['error'] = ', '.join([error['msg'] for error in ex.errors()])
            return TemplateResponse('auth/login.jinja2', context=context, status_code=400)
        
        except HTTPException as ex:
            detail = ex.detail[0]
            context['error'] = detail['msg']
            return TemplateResponse('auth/login.jinja2', context=context, status_code=ex.status_code)

        response = responses.RedirectResponse('/?msg=Successfully-Logged')
        response.set_cookie('token_user', user_token)

        return response
    
    response = TemplateResponse('auth/login.jinja2', context=context)
    response.delete_cookie('token_user')
    
    return response
    


@user_router.get('/logout/')
async def logout(uow: UOWDep, request: Request):
    current_roken= request.cookies.get('token_user')
    await user_service.logout_user(current_token=current_roken, uow=uow)
    response = responses.RedirectResponse('/')
    response.delete_cookie('token_user')
    
    return response



@user_router.get('/reset_password/')
@user_router.post('/reset_password/')
async def reset_password(request: Request, uow: UOWDep, popular: popular, recent: recent):
    context = {'request': request, 'popular': popular, 'recent': recent, 'title': titles['reset_password']}
    
    if request.method == 'POST':
        form = await request.form()
        
        try:
            email = EmailSchema(**form)
            
        except ValidationError as ex:
            context['errors'] = [error['msg']for error in ex.errors()][0]
            return TemplateResponse('auth/reset_password.jinja2', context=context, status_code=400)
        
        try:
            user: OutputUserSchema = await user_service.get_user(uow, email=email.email)
            
        except HTTPException as ex:
            context['error'] = f'user with email: {ex.detail[0]} not register'
            return TemplateResponse('auth/reset_password.jinja2', context=context, status_code=ex.status_code)
        
        token = await user_service.get_reset_token(uid=user.uid)
        await user_service.send_message(url=request.url_for('change_password', token=token), user=user)
        context['success'] = f'SUCCESS!!! Instruction for reset password wa sending on your email {email}'
        
    return  TemplateResponse('auth/reset_password.jinja2', context=context)


@user_router.get('/change_password/{token}')
@user_router.post('/change_password/{token}')
async def change_password(token: str, request: Request, uow: UOWDep, popular: popular, recent: recent):
    context = {'request': request, 'popular': popular, 'recent': recent, 'title': titles['change_password']}
    token = token.encode('utf-8')
    payload = await user_service.get_payload_from_reset_token(token=token)
    user_uid = payload['user_uid']
    
    if request.method == 'POST' and payload:
        form = await request.form()
        
        try:
            password_math = ChangeUserPassword(**form)
        
        except ValidationError as ex:
            context['error'] = 'Пароли не совпадают или вы ничего не ввели'
            return TemplateResponse('auth/change_password.jinja2', context, status_code=400)

        try:
            # user: OutputUserSchema = await user_service.get_user(uow=uow, uid=user_uid)
            await user_service.change_password(user_uid, password_math, uow)
            
        except HTTPException as ex:
            context['error'] = ex.detail[0]
            return TemplateResponse('auth/change_password.jinja2', context, status_code=ex.status_code)
        
        # return TemplateResponse('auth/login.jinja2', context=context, status_code=307)
        return responses.RedirectResponse('/login/', status_code=303)

    return TemplateResponse('auth/change_password.jinja2', context)


