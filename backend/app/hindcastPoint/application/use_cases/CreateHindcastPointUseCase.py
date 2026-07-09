from app.hindcastPoint.domain.models import HindcastPoint  # para el hindcastpoint
from app.hindcastPoint.application.repositories import HindcastPointRepositoryABC
from app.users.domain.models import User  # para el requester

 # para el requester

class CreateHindcasPointtUseCase:
    def __init__(self, repo: HindcastPointRepositoryABC):
        self.repo = repo

    async def execute(self, hindcastPoint: HindcastPoint, requester: User) -> HindcastPoint:
        if not requester.is_admin:
            raise PermissionError("Solo admin puede crear puntos Hindcast")
        return await self.repo.create_hindcastPoint(hindcastPoint)