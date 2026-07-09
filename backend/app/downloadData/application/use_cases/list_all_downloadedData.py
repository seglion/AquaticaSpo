from typing import List
from app.downloadData.domain.models import DownloadedData
from app.downloadData.application.repositories import DownloadedDataRepositoryABC
from app.users.domain.models import User


class ListAllDownloadedDataUseCase:
    def __init__(self, repo: DownloadedDataRepositoryABC):
        self.repo = repo

    async def execute(self, requester: User) -> List[DownloadedData]:
        if not requester.is_admin:
            raise PermissionError("Solo el administrador puede listar todas las descargas")
        return await self.repo.list_all_downloaded_data()