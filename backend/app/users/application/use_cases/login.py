from app.users.application.services import UserService
from app.users.domain.models import User
from typing import Optional

class LoginUseCase:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def execute(self, username: str, password: str) -> Optional[User]:
        user = await self.user_service.authenticate(username, password)
        return user