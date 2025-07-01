from app.users.application.repositories import UserRepositoryABC
from app.users.domain.models import User

class UpdateUserUseCase:
    def __init__(self, user_repo: UserRepositoryABC):
        self.user_repo = user_repo

    async def execute(self, user: User, requester: User) -> User:
        if not requester.is_admin:
            if requester.id != user.id:
                raise PermissionError("No tienes permiso para editar este usuario")
            # Si el usuario no es admin, solo puede cambiar la contraseña
            existing_user = await self.user_repo.get_user_by_id(user.id)
            if existing_user is None:
                raise ValueError("Usuario no encontrado")

            updated_user = User(
                id=existing_user.id,
                username=existing_user.username,
                email=existing_user.email,
                hashed_password=user.hashed_password,  # Solo se permite actualizar la contraseña
                is_admin=existing_user.is_admin,
                is_employee=existing_user.is_employee,
            )
            return await self.user_repo.update_user(updated_user)

        # Si es admin, puede actualizar cualquier dato
        return await self.user_repo.update_user(user)