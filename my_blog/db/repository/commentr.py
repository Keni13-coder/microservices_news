from sqlalchemy import select, update
from db.utils.repository import SQLAlchemyRepository
from apps.postapp.models import Comment, Post

class CommentRepository(SQLAlchemyRepository):
    model = Comment
    
    
    # async def find_all(self, **filter_by):
    #         stmt = select(self.model).join(Post).filter_by(**filter_by)
    #         res = await self.session.execute(stmt)

    #         res =  [row.to_read_model() for row in res.scalars().all()]
    #         return res
        
    async def deactivate_all(self, post_uid):
        stmt = update(self.model).values(is_active=False).filter_by(post_uid=post_uid).returning(self.model.uid)
        res = await self.session.execute(stmt)
        return res.scalars().all()
    