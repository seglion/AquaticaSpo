from typing import List, Optional
from app.downloadData.domain.models import DownloadedData

class DownloadedDataRepositoryABC:
    async def add_downloaded_data(self, downloaded_data: DownloadedData) -> DownloadedData:
        ...

    async def get_downloaded_data_by_id(self, downloaded_data_id: int) -> Optional[DownloadedData]:
        ...

    async def list_downloaded_data_by_point_id(self, point_id: int) -> List[DownloadedData]:
        ...

    async def get_latest_downloaded_data_by_point_id(self, point_id: int) -> Optional[DownloadedData]:
        ...

    async def list_all_downloaded_data(self) -> List[DownloadedData]:
        ...