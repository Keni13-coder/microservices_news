from typing import Annotated
from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, mapped_column, declared_attr
from sqlalchemy import text, ForeignKey
from sqlalchemy_utils import UUIDType
from uuid import uuid4, UUID

dt = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
uidpk = Annotated[UUID, mapped_column(type_= UUIDType, primary_key=True, index=True, default=uuid4)]
pstuid = Annotated[UUID, mapped_column(ForeignKey('post.uid'))]
owruid = Annotated[UUID, mapped_column(ForeignKey('user.uid'))]
iact = Annotated[bool, mapped_column(default=True)]

class Base(DeclarativeBase):
    type_annotatation_map = {
        
    }
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

