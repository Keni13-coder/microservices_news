from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class AbsrtactRepository(ABC):
    @abstractmethod
    async def add_one():
        raise NotImplementedError
    
    @abstractmethod
    async def find_all():
        raise NotImplementedError
    
    @abstractmethod
    async def find_one():
        raise NotImplementedError
    
    @abstractmethod
    async def deactivate_one():
        raise NotImplementedError
    

class SQLAlchemyRepository(AbsrtactRepository):
    model = None
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def add_one(self, data: dict):
            stmt = insert(self.model).values(**data).returning(self.model)
            res = await self.session.execute(stmt)
            return res.scalar_one().to_read_model()
        
    async def find_all(self, limit=1000, offset=0, **filter_by):
            stmt = select(self.model).filter_by(**filter_by).limit(limit).offset(offset)
            res = await self.session.execute(stmt)
            res =  [row.to_read_model() for row in res.scalars().all()]
            return res

    async def find_one(self, **filter_by):
            stmt = select(self.model).filter_by(**filter_by)
            res = await self.session.execute(stmt)
            res =  res.scalar_one().to_read_model()
            return res
    
    async def deactivate_one(self, uid: UUID):
        stmt = update(self.model).values(is_active=False).filter_by(uid=uid).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalar_one()
    
    
    async def edit_one(self, uid: UUID, data: dict):
        stmt = update(self.model).values(**data).filter_by(uid=uid).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalar_one().to_read_model()
    
    
    def __repr__(self) -> str:
        return f'{self.model}'