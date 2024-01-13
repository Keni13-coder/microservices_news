from abc import ABC, abstractmethod
from typing import Type
from db.session import async_session_maker
from db.repository import UserRepository, PostRepository, ViewRepository, CommentRepository, TokenRepository

class IUnitOfWork(ABC):
    user: Type[UserRepository]
    post: Type[PostRepository]
    view: Type[ViewRepository]
    comment: Type[CommentRepository]
    token: Type[TokenRepository]
    
    @abstractmethod
    def __init__(self):
        ...

    @abstractmethod
    async def __aenter__(self):
        ...

    @abstractmethod
    async def __aexit__(self, *args):
        ...

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...
        
        
    
    
class UnitOfWork(IUnitOfWork):
    def __init__(self):
        # импортируем сессию и создаем фарбиру сессий
        self.session_factory = async_session_maker
        
    async def __aenter__(self):
        self.session = self.session_factory()
        self.user = UserRepository(self.session)
        self.post = PostRepository(self.session)
        self.view = ViewRepository(self.session)
        self.comment = CommentRepository(self.session)
        self.token = TokenRepository(session=self.session)

    async def __aexit__(self, *args):
        await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()