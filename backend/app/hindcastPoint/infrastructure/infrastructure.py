from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession  # pylint: disable=import-error
from sqlalchemy.future import select

from app.hindcastPoint.domain.models import HindcastPoint
from app.hindcastPoint.infrastructure.models import HindcastPointORM, orm_to_domain, domain_to_orm

class HindcastPointRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_hindcast_point(
        self,
        latitude: float,
        longitude: float,
        url: str,
        models: Optional[List[str]] = None
    ) -> HindcastPoint:
        hindcast_point = HindcastPoint(
            latitude=latitude,
            longitude=longitude,
            url=url,
            models=models
        )
        hindcast_point_orm = domain_to_orm(hindcast_point)
        self.session.add(hindcast_point_orm)
        await self.session.commit()
        await self.session.refresh(hindcast_point_orm)
        return orm_to_domain(hindcast_point_orm)

    async def get_hindcast_point_by_id(self, hindcast_point_id: int) -> Optional[HindcastPoint]:
        hindcast_point_orm = await self.session.get(HindcastPointORM, hindcast_point_id)
        return orm_to_domain(hindcast_point_orm) if hindcast_point_orm else None

    async def list_hindcast_points(self) -> List[HindcastPoint]:
        result = await self.session.execute(select(HindcastPointORM))
        return [orm_to_domain(hp) for hp in result.scalars().all()]

    async def update_hindcast_point(
        self,
        hindcast_point_id: int,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        url: Optional[str] = None,
        models: Optional[List[str]] = None
    ) -> Optional[HindcastPoint]:
        hindcast_point_orm = await self.session.get(HindcastPointORM, hindcast_point_id)
        if not hindcast_point_orm:
            return None

        if latitude is not None:
            hindcast_point_orm.latitude = latitude
        if longitude is not None:
            hindcast_point_orm.longitude = longitude
        if url is not None:
            hindcast_point_orm.url = url
        if models is not None:
            hindcast_point_orm.models = models

        self.session.add(hindcast_point_orm)
        await self.session.commit()
        await self.session.refresh(hindcast_point_orm)
        return orm_to_domain(hindcast_point_orm)

    async def delete_hindcast_point(self, hindcast_point_id: int) -> bool:
        hindcast_point_orm = await self.session.get(HindcastPointORM, hindcast_point_id)
        if not hindcast_point_orm:
            return False
        await self.session.delete(hindcast_point_orm)
        await self.session.commit()
        return True