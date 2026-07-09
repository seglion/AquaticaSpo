from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession# pylint: disable=import-error
from sqlalchemy.future import select

from app.ports.domain.models import Port
from app.ports.application.services import PortService
from app.ports.infrastructure.models import PortORM, orm_to_domain, domain_to_orm

class PortRepository(PortService):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_port(self, name: str, country: str, latitude: float, longitude: float) -> Port:
        port = Port( name=name, country=country, latitude=latitude, longitude=longitude)
        port_orm = domain_to_orm(port)
        self.session.add(port_orm)
        await self.session.commit()
        await self.session.refresh(port_orm)
        return orm_to_domain(port_orm)

    async def get_port_by_id(self, port_id: int) -> Optional[Port]:
        port_orm = await self.session.get(PortORM, port_id)
        return orm_to_domain(port_orm) if port_orm else None

    async def list_ports(self) -> List[Port]:
        result = await self.session.execute(select(PortORM))
        return [orm_to_domain(p) for p in result.scalars().all()]

    async def update_port(
        self,
        port_id: int,
        name: Optional[str] = None,
        country: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> Optional[Port]:
        port_orm = await self.session.get(PortORM, port_id)
        if not port_orm:
            return None

        if name is not None:
            port_orm.name = name
        if country is not None:
            port_orm.country = country
        if latitude is not None:
            port_orm.latitude = latitude
        if longitude is not None:
            port_orm.longitude = longitude

        self.session.add(port_orm)
        await self.session.commit()
        await self.session.refresh(port_orm)
        return orm_to_domain(port_orm)

    async def delete_port(self, port_id: int) -> bool:
        port_orm = await self.session.get(PortORM, port_id)
        if not port_orm:
            return False
        await self.session.delete(port_orm)
        await self.session.commit()
        return True