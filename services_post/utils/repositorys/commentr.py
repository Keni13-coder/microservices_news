from uuid import UUID
from sqlalchemy import update
from utils.repositorys.abc_repository import SQLAlchemyRepository
from api.models import Comment

class CommentRepository(SQLAlchemyRepository):
    model = Comment
    
        
    async def deactivate_all(self, post_uid: UUID, owner_uid: UUID):
        stmt = update(self.model).values(is_active=False).filter_by(post_uid=post_uid, owner_uid=owner_uid).returning(self.model.uid)
        res = await self.session.execute(stmt)
        return res.scalars().all()
    