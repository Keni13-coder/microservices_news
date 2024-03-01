from datetime import datetime



from sqlalchemy_utils import EmailType, UUIDType
from sqlalchemy.orm import mapped_column, Mapped, relationship


from db.base_class import Base, uidpk, dt, owruid, iact, uuid4, UUID

from schemas import OutputToken, OutputUserSchema


__all__ = ['User', 'Token']


class User(Base):
    uid: Mapped[uidpk]
    create_date: Mapped[dt]
    email: Mapped[str] = mapped_column(type_= EmailType, unique=True)
    username: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    is_active: Mapped[iact]
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
    jti: Mapped[UUID] = mapped_column(type_= UUIDType, primary_key=True, index=True)
    user_uid: Mapped[owruid]
    is_active: Mapped[bool] = mapped_column(default=True)
    device_id:  Mapped[UUID] = mapped_column(type_= UUIDType, default=uuid4)
    
    def to_read_model(self) -> OutputToken:
        return OutputToken(
            jti=self.jti,
            user_uid=self.user_uid,
            is_active= self.is_active,
            device_id= self.device_id
        )