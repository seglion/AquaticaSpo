from app.hindcastPoint.domain.models import HindcastPoint  # modelo del dominio
from app.hindcastPoint.application.repositories import HindcastPointRepositoryABC
from app.users.domain.models import User

from dataclasses import replace

class UpdateHindCastPointUseCase:
    def __init__(self, repo: HindcastPointRepositoryABC):
        self.repo = repo

    async def execute(self, hindcast_point_id: int, updated_data: dict, requester: User) -> HindcastPoint:
        if not requester.is_admin:
            raise PermissionError("Solo admin puede actualizar contratos")

        original = await self.repo.get_hindcastPoint_by_id(hindcast_point_id)
        if original is None:
            raise ValueError("HindcastPoint no encontrado")

        # Crea un nuevo objeto HindcastPoint con los cambios aplicados
        updated_hindcast_point = replace(original, **updated_data)

        # Llama al repo con el objeto actualizado
        updated = await self.repo.update_hindcastPoint(updated_hindcast_point)

        return updated