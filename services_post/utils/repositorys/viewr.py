from sqlalchemy import select, update

from utils.repositorys.abc_repository import SQLAlchemyRepository
from api.models import View

class ViewRepository(SQLAlchemyRepository):
    model = View
    
    
    async def deactivate_one(self) -> ValueError:
        raise ValueError('Views are always active')
    
    
