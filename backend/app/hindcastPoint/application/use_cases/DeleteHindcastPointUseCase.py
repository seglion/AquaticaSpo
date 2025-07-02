from app.hindcastPoint.application.repositories import HindcastPointRepositoryABC
from app.users.domain.models import User  # para el requester

class DeleteHindCastUseCase:
    def __init__(self, repo: HindcastPointRepositoryABC):
        self.repo = repo

    async def execute(self, hindcastPoint_id: int, requester: User) -> None:
        if not isinstance(hindcastPoint_id, int):
            raise TypeError("El ID debe ser un entero")

        if not requester.is_admin:
            raise PermissionError("Solo admin puede borrar puntos Hindcast")
        
        deleted = await self.repo.delete_hindcastPoint(hindcastPoint_id)
        if not deleted:
            raise ValueError("Punto Hindcast no encontrado")