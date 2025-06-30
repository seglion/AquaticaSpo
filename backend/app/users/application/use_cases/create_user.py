from app.users.domain.models import User
from app.users.application.repositories import UserRepositoryABC

class CreateUserUseCase:
    def __init__(self, user_repo: UserRepositoryABC):
        self.user_repo = user_repo

    async def execute(self, user: User, requester: User) -> User:
        if not requester.is_admin:
            raise PermissionError("Solo admin puede crear usuarios")
        return await self.user_repo.create_user(user)