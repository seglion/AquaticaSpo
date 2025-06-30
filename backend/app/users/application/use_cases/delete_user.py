from app.users.application.repositories import UserRepositoryABC
from app.users.domain.models import User

class DeleteUserUseCase:
    def __init__(self, user_repo: UserRepositoryABC):
        self.user_repo = user_repo

    async def execute(self, user_id: int, requester: User) -> None:
        if not requester.is_admin:
            raise PermissionError("Solo admin puede borrar usuarios")
        await self.user_repo.delete_user(user_id)