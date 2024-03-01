import json
from httpx import AsyncClient, Response
from core.config import settings

async def test_add_comment(ac: AsyncClient):
    cookie = {'token_uid': '654014e1c4dc49d49007698f2291f2a7'}
    
    data = json.dumps({
        'content': 'тритий на удачю',
        'post_uid': '6a9fed48-8b35-40a4-a461-b383f33451f5'
    }).encode()
    
    response: Response = await ac.post(f'{settings.PREFIX_API_VERSION}/comment/add-comment/', content=data, cookies=cookie)
    print(response.read().decode())
    
    
async def test_get_comment(ac: AsyncClient):
    cookie = {'token_uid': '654014e1c4dc49d49007698f2291f2a7'}
    params = {'post_uid': '6a9fed48-8b35-40a4-a461-b383f33451f5'}
    response: Response = await ac.get(f'{settings.PREFIX_API_VERSION}/comment/commets-post-all/6a9fed48-8b35-40a4-a461-b383f33451f5/', params=params, cookies=cookie)
    print(response.read().decode())


async def test_update_comment(ac: AsyncClient):
    cookie = {'token_uid': '654014e1c4dc49d49007698f2291f2a7'}
    params = {'comment_uid': 'fd3ee981-05c9-4497-a214-e5b600551f95'}
    data = json.dumps(
        {
            'content': 'все ещё классный пост'
        }
    ).encode()
    response: Response = await ac.put(f'{settings.PREFIX_API_VERSION}/comment/comment-edit/fd3ee981-05c9-4497-a214-e5b600551f95/',content=data, params=params, cookies=cookie)
    print(response.read().decode())
    
    
    
async def test_delete_comment(ac: AsyncClient):
    cookie = {'token_uid': '654014e1c4dc49d49007698f2291f2a7'}
    params = {'comment_uid': 'fd3ee981-05c9-4497-a214-e5b600551f95'}

    response: Response = await ac.delete(f'{settings.PREFIX_API_VERSION}/comment/delete-comment/one/fd3ee981-05c9-4497-a214-e5b600551f95/', params=params, cookies=cookie)
    print(response.read().decode())
    
   
    
async def test_delete_comments_all(ac: AsyncClient):
    cookie = {'token_uid': '654014e1c4dc49d49007698f2291f2a7'}
    params = {'post_uid': '6a9fed48-8b35-40a4-a461-b383f33451f5'}

    response: Response = await ac.delete(f'{settings.PREFIX_API_VERSION}/comment/delete-comment/all/6a9fed48-8b35-40a4-a461-b383f33451f5/', params=params, cookies=cookie)
    print(response.read().decode())