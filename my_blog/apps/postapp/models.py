# from typing import List

from datetime import date
from typing import List

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy.sql.schema import UniqueConstraint

from db.base_class import Base, uidpk, dt, owruid, pstuid, iact
from apps.postapp.schemas import OutputPostSchemas, OutputCommentSchema, OutputViewSchema, OutputUserSchema
# from apps.authapp.models import User

__all__ = ['Post', 'Comment', 'View']
class Post(Base):
    uid: Mapped[uidpk]
    create_date: Mapped[dt]
    is_active: Mapped[iact]
    title: Mapped[str]
    image: Mapped[str]
    content: Mapped[str]
    owner_uid: Mapped[owruid]
    owner = relationship('User', back_populates='post')
    comment = relationship('Comment', back_populates='post')
    view = relationship('View', back_populates='post')
    
    def to_read_model(self, owner: OutputUserSchema=None, comment: List[OutputCommentSchema]=[], view: List[OutputViewSchema]=[]) -> OutputPostSchemas:
        date_ = self.create_date 
        only_date, _ = date_.date(), date_.time()
        return OutputPostSchemas(
            uid=self.uid,
            create_date=only_date,
            is_active=self.is_active,
            title=self.title,
            image=self.image,
            content=self.content,
            owner_uid=self.owner_uid,
            owner=owner,
            comment=comment,
            view=view
        )
    
    
    
class Comment(Base):
    uid: Mapped[uidpk]
    create_date: Mapped[dt]
    content: Mapped[str] = mapped_column(type_=Text)
    post_uid: Mapped[pstuid]
    owner_uid: Mapped[owruid]
    is_active: Mapped[iact]
    post = relationship('Post', back_populates='comment')
    owner = relationship('User', back_populates='comment')
    
    def to_read_model(self, owner: OutputUserSchema=None) -> OutputCommentSchema:
        return OutputCommentSchema(
            uid=self.uid,
            create_date=self.create_date,
            content=self.content,
            post_uid=self.post_uid,
            owner_uid=self.owner_uid,
            owner=owner
        )

class View(Base):
    uid: Mapped[uidpk]
    post_uid: Mapped[pstuid]
    owner_uid: Mapped[owruid]
    post = relationship('Post', back_populates='view')
    owner = relationship('User', back_populates='view')
    __table_args__ = (UniqueConstraint('post_uid', 'owner_uid', name='unique'),)
    
    def to_read_model(self) -> OutputViewSchema:
        return OutputViewSchema(
            uid=self.uid,
            post_uid=self.post_uid,
            owner_uid=self.owner_uid
        )