from tests.conftest import IUnitOfWork
from httpx import AsyncClient







class TestEndPoindAuth:
    async def test_point_register(self, ac: AsyncClient):
        data = {
            'username':'test_user',
            'email':'test_user@mail.ru',
            'password':'test13'}
        
        response = await ac.post('/register/', data=data)
        cookie = response.cookies.get('token_user')
        assert response.status_code == 303
        assert cookie
    
    async def test_point_login(self, ac: AsyncClient):

        data = {
            'email':'test_user@mail.ru',
            'password':'test13'
        }
        
        response = await ac.post('/login/', data=data)
        cookie = response.cookies.get('token_user')
        
        assert response.status_code == 307
        assert cookie
        
    async def test_current_user(self, ac: AsyncClient, get_uow: IUnitOfWork):
        cookie = ac.cookies.get('token_user')
        async with get_uow:
            user = await get_uow.user.find_one(email='test_user@mail.ru')
            token = await get_uow.token.find_one(token=cookie)

        assert user.uid == token.user_uid
        
    
    async def test_point_logout(self, ac: AsyncClient):
        response = await ac.get('/logout/')
        cookie = response.cookies.get('token_user')
        
        assert cookie is None
        
    
    async def test_point_reset_password(self, ac: AsyncClient, celery_worker):
        data = {'email':'test_user@mail.ru'}
        response = await ac.post('/reset_password/', data=data)
        
        assert response.status_code == 200
        
    