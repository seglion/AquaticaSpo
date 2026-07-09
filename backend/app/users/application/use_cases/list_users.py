from typing import List
from app.users.application.repositories import UserRepositoryABC
from app.users.domain.models import User

class ListUsersUseCase:
    def __init__(self, user_repo: UserRepositoryABC):
        self.user_repo = user_repo

    async def execute(self, requester: User) -> List[User]:
        if not requester.is_admin:
            raise PermissionError("Solo admin puede listar usuarios")
        return await self.user_repo.list_users()