from typing import List
from app.downloadData.domain.models import DownloadedData
from app.downloadData.application.repositories import DownloadedDataRepositoryABC
from app.users.domain.models import User


class ListDownloadedDataByPointUseCase:
    def __init__(self, repo: DownloadedDataRepositoryABC):
        self.repo = repo

    async def execute(self, point_id: int, requester: User) -> List[DownloadedData]:
        if not requester.is_admin:
            raise PermissionError("No tiene Permisos de Administrador")
        return await self.repo.list_downloaded_data_by_point_id(point_id)