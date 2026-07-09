from app.downloadData.domain.models import DownloadedData
from app.downloadData.application.repositories import DownloadedDataRepositoryABC
from app.users.domain.models import User


class GetDownloadedDataByIdUseCase:
    def __init__(self, repo: DownloadedDataRepositoryABC):
        self.repo = repo

    async def execute(self, downloaded_data_id: int, requester: User) -> DownloadedData:
        if not requester.is_admin:
            raise PermissionError("Solo admin puede ver datos descargados individuales")
        data = await self.repo.get_downloaded_data_by_id(downloaded_data_id)
        if data is None:
            raise ValueError(f"No se encontró la descarga con id {downloaded_data_id}")
        return data