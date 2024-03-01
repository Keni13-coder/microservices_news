from uuid import UUID
from fastapi import APIRouter
from fastapi_cache.decorator import cache

from utils.service.comment import comment_service
from schemas import (
    CreateCommentSchema,
    UpgradeCommentSchema,
    DefaultMessageOutput,
    OutputCommentModel,
    ResponseUserModel
    )
from utils.dependences import UOWDep, token_cookie, HateoasDEP
from utils.broker import RabbitManagerDep, PostToUserSender
from utils.data_redis import cache_key_builder

router = APIRouter(prefix='/comment', tags=['Comment'])


@router.post('/add-comment/', response_model=DefaultMessageOutput)
async def add_comment(comment: CreateCommentSchema, uow: UOWDep, token_uid: token_cookie, bm: RabbitManagerDep, info_api: HateoasDEP):
    resul: PostToUserSender  = await bm.user_sender.send_get(token=token_uid)
    user: ResponseUserModel = await resul.get_resul(timeout=1.0)
        
    await comment_service.add_comment(comment, uow, owner_uid=user.uid)
    response = DefaultMessageOutput(detail={'message': 'the comment was created'}, info_api=info_api)
    return response


@router.delete('/delete-comment/all/{post_uid}/', response_model=DefaultMessageOutput)
async def delete_post_comments(post_uid: UUID, uow: UOWDep, token_uid: token_cookie, bm: RabbitManagerDep, info_api: HateoasDEP):

    resul: PostToUserSender  = await bm.user_sender.send_get(token=token_uid)
    user: ResponseUserModel = await resul.get_resul(timeout=1.0)
       
    await comment_service.delete_comment_all(post_uid=post_uid, uow=uow, owner_uid=user.uid) 
    
    response = DefaultMessageOutput(detail={'message': 'the comments was deleted'}, info_api=info_api)
    return response
    
@router.delete('/delete-comment/one/{comment_uid}/', response_model=DefaultMessageOutput)
async def delete_comment(comment_uid: UUID, uow: UOWDep, token_uid: token_cookie, bm: RabbitManagerDep, info_api: HateoasDEP):
    resul: PostToUserSender  = await bm.user_sender.send_get(token=token_uid)
    user: ResponseUserModel = await resul.get_resul(timeout=1.0)
         
    await comment_service.delete_comment(comment_uid=comment_uid, uow=uow, owner_uid=user.uid) 
    response = DefaultMessageOutput(detail={'message': 'the comment was deleted'}, info_api=info_api)
    return response


@router.get('/commets-post-all/{post_uid}/', response_model=OutputCommentModel)
@cache(expire=30, key_builder=cache_key_builder)
async def get_comment(post_uid: UUID, uow: UOWDep, info_api: HateoasDEP):
    comments = await comment_service.get_comment_all(post_uid=post_uid, uow=uow)
    response = OutputCommentModel(detail={'response_object': comments}, info_api=info_api)
    return response


@router.put('/comment-edit/{comment_uid}/', response_model=DefaultMessageOutput)
async def update_comment(comment_uid: UUID, comment_data: UpgradeCommentSchema, uow: UOWDep, token_uid: token_cookie, bm: RabbitManagerDep, info_api: HateoasDEP):
    resul: PostToUserSender  = await bm.user_sender.send_get(token=token_uid)
    user: ResponseUserModel = await resul.get_resul(timeout=1.0)
        
    await comment_service.update_comment(comment_uid=comment_uid, comment_data=comment_data, uow=uow, owner_uid=user.uid)
    response = DefaultMessageOutput(detail={'message': 'the comment was updated'}, info_api=info_api)
    return response