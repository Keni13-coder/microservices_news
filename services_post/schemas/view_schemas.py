from typing import Optional
from pydantic import UUID4, BaseModel


class ViewBase(BaseModel):
    class Config:
        from_attributes=True
    
class CreateViewSchema(ViewBase):
    post_uid: UUID4



        
class OutputViewSchema(ViewBase):
    uid: Optional[UUID4]
    post_uid: Optional[UUID4] 
    owner_uid: Optional[UUID4]