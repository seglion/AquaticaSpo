from app.users.application.repositories import UserRepositoryABC
from app.users.domain.models import User

class UpdateUserUseCase:
    def __init__(self, user_repo: UserRepositoryABC):
        self.user_repo = user_repo

    async def execute(self, user: User, requester: User) -> User:
        if not requester.is_admin and requester.id != user.id:
            raise PermissionError("No tienes permiso para editar este usuario")
        return await self.user_repo.update_user(user)