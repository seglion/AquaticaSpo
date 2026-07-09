from app.users.domain.models import User
from abc import ABC, abstractmethod


class UserService(ABC):

    @abstractmethod
    async def login(self, user: str, password: str) -> User:
        raise NotImplementedError
