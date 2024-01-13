from sqlalchemy import select, insert, or_
from uuid import UUID
from fastapi import HTTPException
from fastapi_cache.decorator import cache

from apps.authapp.models import User, Token
from db.utils.repository import SQLAlchemyRepository
from db.utils.cache_builder import cache_key_builder, CostumCoder

class UserRepository(SQLAlchemyRepository):
    model = User
    
    @cache(expire=5, key_builder=cache_key_builder, coder=CostumCoder)
    async def _get_user_by_token(self, token: UUID):
        query = select(User).join(Token).filter(Token.token == token)
        user = await self.session.execute(query)
        return user.scalar_one().to_read_model()
    
    
    async def add_one(self, data: dict):
        email = data['email']
        username = data['username']
        valid_query = select(self.model).filter(or_(self.model.email == email, self.model.username == username))
        valid_query = await self.session.execute(valid_query)
        valid_query= valid_query.scalars().all()
        if not valid_query:
            stmt = insert(self.model).values(**data).returning(self.model)
            res = await self.session.execute(stmt)
            return res.scalar_one().to_read_model()
        er = [{'type': 'value_error', 'loc': (), 'msg': "Value error, 'The given name or email address is already busy' is not a valid HTTPStatus", 'input': {}}]
        raise HTTPException(status_code=409, detail=er)
    
    
