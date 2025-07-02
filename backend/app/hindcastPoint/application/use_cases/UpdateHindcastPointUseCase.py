
from app.hindcastPoint.domain.models import HindcastPoint  # para el hindcastpoint
from app.hindcastPoint.application.repositories import HindcastPointRepositoryABC
from app.users.domain.models import User  # para el requester

class UpdateHindCastPointUseCase:
    def __init__(self, repo: HindcastPointRepositoryABC):
        self.repo = repo

    async def execute(self, hindcastPoint: HindcastPoint, requester: User) -> HindcastPoint:
        if not isinstance(hindcastPoint, HindcastPoint):
            raise TypeError("hindcastPoint debe ser instancia de HindcastPoint")
        if not requester.is_admin:
            raise PermissionError("Solo admin puede actualizar contratos")
        return await self.repo.update_hindcastPoint(hindcastPoint)