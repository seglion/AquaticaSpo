from typing import Optional
from app.users.application.repositories import UserRepositoryABC
from app.users.domain.models import User

class GetUserUseCase:
    def __init__(self, user_repo: UserRepositoryABC):
        self.user_repo = user_repo

    async def execute(self, user_id: int, requester: User) -> Optional[User]:
        if not requester.is_admin and requester.id != user_id:
            raise PermissionError("No tienes permiso para ver este usuario")
        return await self.user_repo.get_user_by_id(user_id)