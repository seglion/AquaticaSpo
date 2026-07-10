from typing import Optional
from app.hindcastPoint.domain.models import HindcastPoint
from app.hindcastPoint.application.repositories import HindcastPointRepositoryABC
from app.users.domain.models import User

class GetContractUseCase:
    def __init__(self, repo: HindcastPointRepositoryABC):
        self.repo = repo

    async def execute(self, hindcastPoint_id: int, requester: Optional[User]) -> Optional[HindcastPoint]:
        # Lectura permitida a cualquier usuario autenticado: el visor necesita el
        # punto de partida (lat/lon/modelos) del sistema de su contrato. El router
        # ya exige login (get_current_user). No es un dato sensible por cliente.
        if requester is None:
            raise PermissionError("Debe estar autenticado para ver Puntos Hindcast")

        if not isinstance(hindcastPoint_id, int):
            raise TypeError("El id debe ser un entero")

        return await self.repo.get_hindcastPoint_by_id(hindcastPoint_id)