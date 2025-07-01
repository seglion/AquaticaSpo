from app.users.infrastructure.repositories import UserRepositoryABC
from app.shared.auth.password_hasher import verify_password
from app.users.domain.models import User
from typing import Optional

class UserService:
    def __init__(self, repo: UserRepositoryABC):
        self.repo = repo

    async def authenticate(self, username: str, password: str) -> Optional[User]:
        user = await self.repo.get_user_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user