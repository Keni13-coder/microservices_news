# from celery.contrib.testing.worker import TestWorkController
from httpx import Response, AsyncClient
from core.config import settings




async def test_create_post(ac: AsyncClient, celery_worker):
    file_path = './tests/fake_images/NewCapture001.png'

    data = {
        "title": "string",
        "content": "string",
    }
        
    cookie = {'token_uid': '654014e1c4dc49d49007698f2291f2a7'}
    response: Response = await ac.post(f'{settings.PREFIX_API_VERSION}/add-post/', data=data, files={'image': ('NewCapture001.png', open(file_path, 'rb'), 'image/png')}, cookies=cookie) # headers=headers,
    print(response.read().decode())
    
    assert 1 == 1
    

async def test_edit_post(ac: AsyncClient, celery_worker):
    file_path = './tests/fake_images/Warface_sample.jpg'

    data = {
        "title": "Пупа",
    }    
    cookie = {'token_uid': '654014e1c4dc49d49007698f2291f2a7'}
    param = {'uuid': '6a9fed48-8b35-40a4-a461-b383f33451f5'}
    response: Response = await ac.put(f'{settings.PREFIX_API_VERSION}/edit/6a9fed48-8b35-40a4-a461-b383f33451f5/', data=data, files={'image': ('Warface_sample.jpg', open(file_path, 'rb'), 'image/jpeg')}, cookies=cookie, params=param) # headers=headers,
    print(response.read().decode())
    
    assert 1 == 1
    
    
async def test_get_posts(ac: AsyncClient):
    response: Response = await ac.get('/post/posts-views-comments/')
    print(response.read().decode())
    
async def test_get_one_post(ac: AsyncClient):
    params = {'uuid': '6a9fed48-8b35-40a4-a461-b383f33451f5'}
    response: Response = await ac.get(f'{settings.PREFIX_API_VERSION}/one-post/{"6a9fed48-8b35-40a4-a461-b383f33451f5"}/', params=params)
    print(response.read().decode())
    
    
async def test_delete_post(ac: AsyncClient):
    params = {'uuid': '8f9ff56d-23e2-4bc0-97c3-1f49b5c8a003'}
    cookies = {'token_uid': '654014e1c4dc49d49007698f2291f2a7'}
    response: Response = await ac.delete(f'{settings.PREFIX_API_VERSION}/remove/{"8f9ff56d-23e2-4bc0-97c3-1f49b5c8a003"}/', params=params, cookies=cookies)
    print(response.read().decode())
   