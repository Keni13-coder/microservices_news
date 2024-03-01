from datetime import datetime
from typing import Any, Optional
from pydantic import UUID4, BaseModel


class CommentBase(BaseModel):
    content: str
    post_uid: UUID4
   
    class Config:
        from_attributes=True
        
        
class CreateCommentSchema(CommentBase):
    pass


class UpgradeCommentSchema(BaseModel):
    content: str
    

class OutputCommentSchema(CommentBase):
    uid: Optional[UUID4]
    create_date: Optional[datetime]
    content: Optional[str]
    post_uid: Optional[UUID4]
    owner_uid: Optional[UUID4]
    
    
    
