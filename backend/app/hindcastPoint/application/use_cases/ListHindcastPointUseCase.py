from typing import List
from app.hindcastPoint.domain.models import HindcastPoint  # para el hindcastpoint
from app.hindcastPoint.application.repositories import HindcastPointRepositoryABC
from app.users.domain.models import User  # para el requester

class ListHindCastPointUseCase:
    def __init__(self, repo: HindcastPointRepositoryABC):
        self.repo = repo

    async def execute(self, requester: User) -> List[HindcastPoint]:
        if not requester or not hasattr(requester, "is_admin") or not requester.is_admin:
            raise PermissionError("Solo admin puede ver Puntos Hindcast")

        return await self.repo.list_hindcastPoint()