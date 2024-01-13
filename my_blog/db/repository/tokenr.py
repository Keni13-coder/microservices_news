from sqlalchemy import delete, select

from uuid import UUID
from db.utils.repository import SQLAlchemyRepository
from apps.authapp.models import Token, User

class TokenRepository(SQLAlchemyRepository):
    model = Token
        
    async def deactivate_one(self, token):
        stmt = delete(self.model).filter_by(token=token).returning(self.model.uid)
        token_uid = await self.session.execute(stmt)
        return token_uid.scalar_one()
    
    async def get_token_by_user(self, user_uid: UUID):
        query = select(Token).join(User).filter(User.uid == user_uid)
        token = await self.session.execute(query)
        return token.scalar_one().to_read_model()

