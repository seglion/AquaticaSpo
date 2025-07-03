# app/forecast_zones/infrastructure/repositories.py
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

from app.forecast_zones.application.repositories import ForecastZoneRepositoryABC
from app.forecast_zones.domain.models import ForecastZone
from app.forecast_zones.infrastructure.models import ForecastZoneORM, orm_to_domain, domain_to_orm

# Importamos ForecastSystemORM si lo necesitamos para uniones o validaciones futuras
# Aunque no se usa directamente en este repositorio simple, es bueno tener la referencia.
# from app.forecast_systems.infrastructure.models import ForecastSystemORM 


class ForecastZoneRepository(ForecastZoneRepositoryABC):
    """
    Implementación concreta de ForecastZoneRepositoryABC utilizando SQLAlchemy.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_forecast_zone(self, zone: ForecastZone) -> ForecastZone:
        """Crea una nueva zona de previsión en la base de datos."""
        orm_zone = domain_to_orm(zone)
        self.session.add(orm_zone)
        await self.session.flush() # Para obtener el ID generado por la BD antes del commit
        await self.session.refresh(orm_zone) # Para cargar cualquier campo por defecto (ej. created_at)
        return orm_to_domain(orm_zone)

    async def get_forecast_zone_by_id(self, zone_id: int) -> Optional[ForecastZone]:
        """Obtiene una zona de previsión por su ID."""
        stmt = select(ForecastZoneORM).where(ForecastZoneORM.id == zone_id)
        result = await self.session.execute(stmt)
        orm_zone = result.scalars().first()
        return orm_to_domain(orm_zone) if orm_zone else None

    async def list_forecast_zones(self) -> List[ForecastZone]:
        """Lista todas las zonas de previsión existentes."""
        stmt = select(ForecastZoneORM)
        result = await self.session.execute(stmt)
        orm_zones = result.scalars().all()
        return [orm_to_domain(zone) for zone in orm_zones]

    async def update_forecast_zone(self, zone: ForecastZone) -> ForecastZone:
        """Actualiza una zona de previsión existente."""
        # Primero, recupera la zona existente para asegurar que está en la sesión
        # y para que SQLAlchemy pueda rastrear los cambios.
        existing_orm_zone_stmt = select(ForecastZoneORM).where(ForecastZoneORM.id == zone.id)
        result = await self.session.execute(existing_orm_zone_stmt)
        existing_orm_zone = result.scalars().first()

        if not existing_orm_zone:
            # Esto puede ocurrir si el objeto ForecastZone del dominio no se obtuvo
            # de la base de datos y se intentan actualizar campos que no están trackeados.
            # O si el ID no existe.
            raise ValueError(f"Zona de previsión con ID {zone.id} no encontrada para actualizar.")

        # Actualiza los atributos del objeto ORM existente
        existing_orm_zone.name = zone.name
        existing_orm_zone.description = zone.description
        existing_orm_zone.forecast_system_id = zone.forecast_system_id
        
        # Convierte el GeoJSON del dominio a la representación de geoalchemy2
        from app.forecast_zones.infrastructure.models import domain_to_orm # Importar aquí para evitar circular
        temp_orm_obj = domain_to_orm(zone)
        existing_orm_zone.geom = temp_orm_obj.geom # Asigna el objeto geom de geoalchemy2
        
        await self.session.flush() # Guarda los cambios
        await self.session.refresh(existing_orm_zone) # Refresca para asegurar datos actualizados (ej. updated_at si existiera)
        return orm_to_domain(existing_orm_zone)

    async def delete_forecast_zone(self, zone_id: int) -> bool:
        """
        Elimina una zona de previsión por su ID.
        Retorna True si se eliminó, False en caso contrario.
        """
        stmt = delete(ForecastZoneORM).where(ForecastZoneORM.id == zone_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0 # Retorna True si se eliminó al menos una fila

    async def list_forecast_zones_by_forecast_system_id(self, system_id: int) -> List[ForecastZone]:
        """Lista las zonas de previsión asociadas a un sistema de previsión específico."""
        stmt = select(ForecastZoneORM).where(ForecastZoneORM.forecast_system_id == system_id)
        result = await self.session.execute(stmt)
        orm_zones = result.scalars().all()
        return [orm_to_domain(zone) for zone in orm_zones]