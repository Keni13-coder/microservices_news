from sqlalchemy import delete, select, update

from uuid import UUID
from utils.repositorys.abc_repository import SQLAlchemyRepository
from api.models import Token, User

class TokenRepository(SQLAlchemyRepository):
    model = Token
        
    async def delete_all(self, **filtres) -> None:
        stmt = delete(self.model).filter_by(**filtres)
        await self.session.execute(stmt)
        
    async def deactivate_all(self, **filtres) -> None:
        stmt = update(self.model).values(is_active=False).filter_by(**filtres)
        await self.session.execute(stmt)
        
    
    async def get_token_by_user(self, user_uid: UUID):
        query = select(Token).join(User).filter(User.uid == user_uid)
        token = await self.session.execute(query)
        return token.scalar_one().to_read_model()

