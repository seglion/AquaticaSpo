from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.downloadData.domain.models import DownloadedData
from app.downloadData.infrastructure.models import DownloadedDataORM, orm_to_domain, domain_to_orm
from app.downloadData.application.repositories import DownloadedDataRepositoryABC


class DownloadedDataRepository(DownloadedDataRepositoryABC):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_downloaded_data(self, downloaded_data: DownloadedData) -> DownloadedData:
        downloaded_data_orm = domain_to_orm(downloaded_data)
        self.session.add(downloaded_data_orm)
        await self.session.commit()
        await self.session.refresh(downloaded_data_orm)
        return orm_to_domain(downloaded_data_orm)

    async def get_downloaded_data_by_id(self, downloaded_data_id: int) -> Optional[DownloadedData]:
        downloaded_data_orm = await self.session.get(DownloadedDataORM, downloaded_data_id)
        return orm_to_domain(downloaded_data_orm) if downloaded_data_orm else None

    async def get_latest_downloaded_data_by_point_id(self, point_id: int) -> Optional[DownloadedData]:
        query = (
            select(DownloadedDataORM)
            .where(DownloadedDataORM.point_id == point_id)
            .order_by(DownloadedDataORM.downloaded_at.desc())
            .limit(1)
        )
        result = await self.session.execute(query)
        latest_orm = result.scalars().first()
        return orm_to_domain(latest_orm) if latest_orm else None

    async def list_all_downloaded_data(self) -> List[DownloadedData]:
        result = await self.session.execute(select(DownloadedDataORM))
        return [orm_to_domain(dd) for dd in result.scalars().all()]

    async def list_downloaded_data_by_point_id(self, point_id: int) -> List[DownloadedData]:
        query = select(DownloadedDataORM).where(DownloadedDataORM.point_id == point_id)
        result = await self.session.execute(query)
        return [orm_to_domain(dd) for dd in result.scalars().all()]

    async def update_downloaded_data(self, downloaded_data: DownloadedData) -> Optional[DownloadedData]:
        downloaded_data_orm = await self.session.get(DownloadedDataORM, downloaded_data.id)
        if not downloaded_data_orm:
            return None

        # Actualiza los campos que tenga el modelo domain
        downloaded_data_orm.point_id = downloaded_data.point_id
        downloaded_data_orm.downloaded_at = downloaded_data.downloaded_at
        downloaded_data_orm.data = downloaded_data.data

        self.session.add(downloaded_data_orm)
        await self.session.commit()
        await self.session.refresh(downloaded_data_orm)
        return orm_to_domain(downloaded_data_orm)

    async def delete_downloaded_data(self, downloaded_data_id: int) -> None:
        downloaded_data_orm = await self.session.get(DownloadedDataORM, downloaded_data_id)
        if downloaded_data_orm:
            await self.session.delete(downloaded_data_orm)
            await self.session.commit()