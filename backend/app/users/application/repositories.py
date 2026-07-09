from abc import ABC, abstractmethod
from typing import Optional, List
from app.users.domain.models import User

class UserRepositoryABC(ABC):
    @abstractmethod
    async def create_user(self, user: User) -> User:
        ...

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        ...

    @abstractmethod
    async def get_user_by_username(self, username: str) -> Optional[User]:
        ...

    @abstractmethod
    async def update_user(self, user: User) -> User:
        ...

    @abstractmethod
    async def delete_user(self, user_id: int) -> None:
        ...

    @abstractmethod
    async def list_users(self) -> List[User]:
        ...