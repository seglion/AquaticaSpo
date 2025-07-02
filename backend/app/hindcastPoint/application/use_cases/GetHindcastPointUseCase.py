from typing import Optional
from app.hindcastPoint.domain.models import HindcastPoint
from app.hindcastPoint.application.repositories import HindcastPointRepositoryABC
from app.users.domain.models import User

class GetContractUseCase:
    def __init__(self, repo: HindcastPointRepositoryABC):
        self.repo = repo

    async def execute(self, hindcastPoint_id: int, requester: Optional[User]) -> Optional[HindcastPoint]:
        if requester is None or not getattr(requester, "is_admin", False):
            raise PermissionError("Solo admin puede ver Puntos Hindcast")

        if not isinstance(hindcastPoint_id, int):
            raise TypeError("El id debe ser un entero")

        return await self.repo.get_hindcastPoint_by_id(hindcastPoint_id)