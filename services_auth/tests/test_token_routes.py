import json
import asyncio
from httpx import AsyncClient, Response
from core.config import settings
from typing import Literal, TypedDict

'''
post('/'
post('/refresh/
delete('/del-token/'
'''
class TokenResponse(TypedDict):
    access_token: str
    token_type: Literal['bearer'] = 'bearer'
    info_api: dict

HEADER = {}
COOKIE = {}

TIME_OUT = settings.ACCESS_TOREN_EXPIRE + 1

async def test_login(ac: AsyncClient):
    global HEADER, COOKIE
    data_form = {'username': 'user@example.com', 'password': '1313'}
    response: Response = await ac.post(f'{settings.PREFIX_API_VERSION}/token/', data=data_form)
    tokens: TokenResponse = json.loads(response.read().decode())
    COOKIE['refresh_token'] = response.cookies.get('refresh_token')
    HEADER['authorization'] = f"{tokens['token_type']} {tokens['access_token']}"
    assert 'OK'
    
async def test_refresh_token(ac: AsyncClient):
    await asyncio.sleep(TIME_OUT)
    
    response: Response = await ac.post(f'{settings.PREFIX_API_VERSION}/token/refresh/', headers=HEADER, cookies=COOKIE)
    tokens: TokenResponse = response.read().decode()
    print(tokens)
    assert 'OK'
    
    
async def test_logout(ac: AsyncClient):
    ...
    
    
    