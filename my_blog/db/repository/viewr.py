from sqlalchemy import select, update

from db.utils.repository import SQLAlchemyRepository
from apps.postapp.models import View, Post

class ViewRepository(SQLAlchemyRepository):
    model = View
    
    
    async def deactivate_one(self) -> ValueError:
        raise ValueError('Views are always active')
    
    
    # async def find_all(self, **filter_by):
    #         stmt = select(self.model).join(Post).filter_by(**filter_by)
    #         res = await self.session.execute(stmt)

    #         res =  [row.to_read_model() for row in res.scalars().all()]
    #         return res