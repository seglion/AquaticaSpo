from app.users.application.repositories import UserRepositoryABC
from app.users.domain.models import User

class ChangePasswordUseCase:
    def __init__(self, user_repo: UserRepositoryABC):
        self.user_repo = user_repo

    async def execute(self, user_id: int, new_password_hash: str, requester: User) -> User:
        if not requester.is_admin and requester.id != user_id:
            raise PermissionError("No tienes permiso para cambiar esta contraseña")
        
        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        
        user.hashed_password = new_password_hash
        return await self.user_repo.update_user(user)