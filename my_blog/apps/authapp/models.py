from datetime import datetime



from sqlalchemy_utils import EmailType, UUIDType
from sqlalchemy.orm import mapped_column, Mapped, relationship


from db.base_class import Base, uidpk, dt, owruid, iact, uuid4, UUID

from apps.authapp.schemas import OutputToken, OutputUserSchema
# from apps.postapp.models import Post, Comment, View

__all__ = ['User', 'Token']


class User(Base):
    uid: Mapped[uidpk]
    create_date: Mapped[dt]
    email: Mapped[str] = mapped_column(type_= EmailType, unique=True)
    username: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    is_active: Mapped[iact]
    post = relationship('Post', back_populates='owner')
    comment = relationship('Comment', back_populates='owner')
    view = relationship('View', back_populates='owner')
    # функция для создания токена при смене пароля, при этом токен живет 30 минут
        
        
    def to_read_model(self) -> OutputUserSchema:
        return OutputUserSchema(
            uid=self.uid,
            create_date=self.create_date,
            email=self.email,
            username=self.username,
            hashed_password=self.hashed_password,
            is_active=self.is_active
        )
    
    
class Token(Base):
    uid: Mapped[uidpk]
    token: Mapped[UUID] = mapped_column(type_=UUIDType ,unique=True, nullable=False, index=True, default=uuid4)
    expires: Mapped[datetime]
    user_uid: Mapped[owruid]
    
    def to_read_model(self) -> OutputToken:
        return OutputToken(
            uid=self.uid,
            token=self.token,
            expires=self.expires,
            user_uid=self.user_uid
        )