import json
from httpx import AsyncClient
from fastapi import Response
from core.config import settings

async def test_add_veiw(ac: AsyncClient):
    cookie = {'token_uid': '654014e1c4dc49d49007698f2291f2a7'}
    
    data = json.dumps({
        'post_uid': '6a9fed48-8b35-40a4-a461-b383f33451f5'
    }).encode()
    
    response: Response = await ac.post(f'{settings.PREFIX_API_VERSION}/view/add-view/', content=data, cookies=cookie)
    print(response.read().decode())
    
    
async def test_get_veiw(ac: AsyncClient):  
    params= {'post_uid': '6a9fed48-8b35-40a4-a461-b383f33451f5'}
    response: Response = await ac.get(f'{settings.PREFIX_API_VERSION}/view/views-post-all/6a9fed48-8b35-40a4-a461-b383f33451f5/', params=params)
    print(response.read().decode())
    
    
