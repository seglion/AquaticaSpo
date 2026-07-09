from app.downloadData.domain.models import DownloadedData
from app.downloadData.application.repositories import DownloadedDataRepositoryABC
from app.users.domain.models import User


class AddDownloadedDataUseCase:
    def __init__(self, repo: DownloadedDataRepositoryABC):
        self.repo = repo

    async def execute(self, downloaded_data: DownloadedData, requester: User) -> DownloadedData:
        if not requester.is_admin:
            raise PermissionError("No tiene permisos de Administrador")
        return await self.repo.add_downloaded_data(downloaded_data)