from app.downloadData.domain.models import DownloadedData
from app.downloadData.application.repositories import DownloadedDataRepositoryABC
from app.users.domain.models import User


class GetLatestDownloadedDataByPointUseCase:
    def __init__(self, repo: DownloadedDataRepositoryABC):
        self.repo = repo

    async def execute(self, point_id: int, requester: User) -> DownloadedData:
        if not requester.is_admin:
            raise PermissionError("No tiene permisos de Administrador")
        data = await self.repo.get_latest_downloaded_data_by_point_id(point_id)
        if data is None:
            raise ValueError(f"No se encontró descarga para el punto id {point_id}")
        return data