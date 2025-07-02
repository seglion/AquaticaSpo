from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.hindcastPoint.domain.models import HindcastPoint
from app.hindcastPoint.infrastructure.models import HindcastPointORM, orm_to_domain, domain_to_orm
from app.hindcastPoint.application.repositories import HindcastPointRepositoryABC  # Asegúrate de importar correctamente

class HindcastPointRepository(HindcastPointRepositoryABC):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_hindcastPoint(self, hindcastpoint: HindcastPoint) -> HindcastPoint:
        hindcast_point_orm = domain_to_orm(hindcastpoint)
        self.session.add(hindcast_point_orm)
        await self.session.commit()
        await self.session.refresh(hindcast_point_orm)
        return orm_to_domain(hindcast_point_orm)

    async def get_hindcastPoint_by_id(self, hindcastpoint_id: int) -> Optional[HindcastPoint]:
        hindcast_point_orm = await self.session.get(HindcastPointORM, hindcastpoint_id)
        return orm_to_domain(hindcast_point_orm) if hindcast_point_orm else None

    async def list_hindcastPoint(self) -> List[HindcastPoint]:
        result = await self.session.execute(select(HindcastPointORM))
        return [orm_to_domain(hp) for hp in result.scalars().all()]

    async def update_hindcastPoint(self, hindcastpoint: HindcastPoint) -> HindcastPoint:
        hindcast_point_orm = await self.session.get(HindcastPointORM, hindcastpoint.id)
        if not hindcast_point_orm:
            return None

        hindcast_point_orm.latitude = hindcastpoint.latitude
        hindcast_point_orm.longitude = hindcastpoint.longitude
        hindcast_point_orm.url = hindcastpoint.url
        hindcast_point_orm.models = hindcastpoint.models

        self.session.add(hindcast_point_orm)
        await self.session.commit()
        await self.session.refresh(hindcast_point_orm)
        return orm_to_domain(hindcast_point_orm)

    async def delete_hindcastPoint(self, hindcastpoint_id: int) -> None:
        hindcast_point_orm = await self.session.get(HindcastPointORM, hindcastpoint_id)
        if hindcast_point_orm:
            await self.session.delete(hindcast_point_orm)
            await self.session.commit()
