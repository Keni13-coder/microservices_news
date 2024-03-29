from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi_cache.decorator import cache

from utils.data_redis import cache_key_builder, CostumCoder
from utils.repositorys.abc_repository import SQLAlchemyRepository
from api.models import Post



class PostRepository(SQLAlchemyRepository):
    model = Post
    
    @cache(expire=5, key_builder=cache_key_builder, coder=CostumCoder)
    async def find_one(self, uid):
        stmt = (
            select(self.model)
            .filter_by(uid=uid, is_active=True)
            .options(
                selectinload(self.model.comment),
                selectinload(self.model.view),
            )
            )
        res = await self.session.execute(stmt)
        res =  res.scalar_one()
        res = res.to_read_model(res.comment, res.view) 
        return res
    
    @cache(expire=5, key_builder=cache_key_builder, coder=CostumCoder)
    async def find_all(self, limit=1000, offset=0, **filter_by):
        stmt = (
            select(self.model)
            .filter_by(owner_uid=UUID('210d4ac9-90aa-4516-9185-94ffc310de43'), is_active=True)
            .options(
            selectinload(self.model.comment),
            selectinload(self.model.view),
            )
            .order_by(self.model.create_date.desc())
            .limit(limit)
            .offset(offset)
        )

        res = await self.session.execute(stmt)
        res =  [row.to_read_model(row.comment, row.view) for row in res.scalars().all()]
        return res
    
    
    
    @cache(expire=60, key_builder=cache_key_builder, coder=CostumCoder)
    async def recent(self, limit=5):
        stmt = (
            select(self.model)
            .where(self.model.is_active==True)
            .options(
                selectinload(self.model.comment),
                selectinload(self.model.view),
            )
            .order_by(self.model.create_date.desc())
            .limit(limit)
            )

        res = await self.session.execute(stmt)

        res =  [row.to_read_model(row.comment, row.view) for row in res.scalars().all()]
 
        return res
    
    @cache(expire=60, key_builder=cache_key_builder, coder=CostumCoder)
    async def popular(self, limit=5):
        stmt = (
            select(self.model)
            .where(self.model.is_active==True)
            .options(
                selectinload(self.model.comment),
                selectinload(self.model.view),
            )
            )

        res = await self.session.execute(stmt)
        res = (row for row in res.scalars().all())
        res =  sorted(res, key=lambda row: (len(row.view), len(row.comment)), reverse=True)
        res = [row.to_read_model(row.comment, row.view) for row in res][:limit]
        return res
    
