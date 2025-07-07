# app/forecast_systems/infrastructure/repositories.py

from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.orm import selectinload
from app.forecastSystems.application.repositories import ForecastSystemRepositoryABC
from app.forecastSystems.domain.models import ForecastSystem
# Eliminamos la importación de update_orm_from_domain
from app.forecastSystems.infrastructure.models import ForecastSystemORM, orm_to_domain, domain_to_orm


class SqlAlchemyForecastSystemRepository(ForecastSystemRepositoryABC):
    async def getForecastSystemByContractId(self, contract_id: int) -> Optional[ForecastSystem]:
        """
        Obtiene un sistema de previsión por el ID de un contrato asociado.
        Retorna None si no se encuentra ningún sistema asociado a ese contrato.
        """
        stmt = select(ForecastSystemORM).where(ForecastSystemORM.contract_id == contract_id)
        result = await self.session.execute(stmt)
        orm_system = result.scalars().first()
        return orm_to_domain(orm_system) if orm_system else None
    """
    Concrete implementation of ForecastSystemRepositoryABC using SQLAlchemy.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def createForecastSystem(self, system: ForecastSystem) -> ForecastSystem:
        """Creates a new forecast system in the database."""
        orm_system = domain_to_orm(system)
        self.session.add(orm_system)
        await self.session.flush() # Flushes changes to get the ID back from the DB
        await self.session.refresh(orm_system) # Refreshes the ORM object with any default values (e.g., auto-generated ID)
        return orm_to_domain(orm_system)

    async def getForecastSystemById(self, system_id: int) -> Optional[ForecastSystem]:
        """Gets a forecast system by its ID."""
        stmt = select(ForecastSystemORM).where(ForecastSystemORM.id == system_id)
        result = await self.session.execute(stmt)
        orm_system = result.scalars().first()
        return orm_to_domain(orm_system) if orm_system else None

    async def getAllForecastSystems(self) -> List[ForecastSystem]:
        """Lists all existing forecast systems."""
        stmt = select(ForecastSystemORM)
        result = await self.session.execute(stmt)
        # Usar .unique() para evitar duplicados por joined eager loading
        orm_systems = result.unique().scalars().all()
        return [orm_to_domain(system) for system in orm_systems]

    async def updateForecastSystem(self, system: ForecastSystem) -> ForecastSystem:
        """
        Updates an existing forecast system.
        Since update_orm_from_domain is removed, we re-create the ORM object.
        """
        # 1. Retrieve the existing ORM object to ensure it exists
        existing_orm_system_stmt = select(ForecastSystemORM).where(ForecastSystemORM.id == system.id)
        result = await self.session.execute(existing_orm_system_stmt)
        existing_orm_system = result.scalars().first()

        if not existing_orm_system:
            raise ValueError(f"Sistema de previsión con ID {system.id} no encontrado para actualizar.")

        # 2. Convert the domain object to a *new* ORM object, preserving the ID
        # The domain_to_orm function should be able to handle an ID if provided
        updated_orm_system = domain_to_orm(system)

        # 3. Add the updated ORM object to the session.
        # This will either merge it (if it's a detached instance with an ID)
        # or potentially mark it for an update if SQLAlchemy detects it.
        # For simplicity and clarity when avoiding `update_orm_from_domain`,
        # a common pattern might be to delete the old one and add the new one,
        # but merging is generally preferred by SQLAlchemy if the ID is present.
        # Let's rely on session.merge() or session.add() if the ORM has the ID.
        # If the ID is already present, session.add() will implicitly act as a merge or update.
        self.session.add(updated_orm_system) # SQLAlchemy will intelligently merge if ID exists

        # If you were strictly deleting and re-adding, it would look more like this:
        # await self.session.delete(existing_orm_system)
        # self.session.add(updated_orm_system)
        # This is generally less efficient due to potential integrity constraints.
        # Relying on `session.add` with a populated ID, or `session.merge` is better.
        # `session.add()` will work correctly here assuming `domain_to_orm` correctly sets the ID
        # on the new ORM object if the domain object already had one.

        await self.session.flush() # Persist changes to the database
        await self.session.refresh(updated_orm_system) # Refresh to ensure any DB-side updates are loaded (e.g. updated_at)
        return orm_to_domain(updated_orm_system)


    async def deleteForecastSystem(self, system_id: int) -> bool:
        """
        Deletes a forecast system by its ID.
        Returns True if deleted, False otherwise.
        """
        stmt = delete(ForecastSystemORM).where(ForecastSystemORM.id == system_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def get_forecast_system_by_contract_id(self, contract_id: int) -> Optional[ForecastSystem]:
        """
        Implementación para obtener un ForecastSystem dado el ID de un contrato.
        """
        stmt = (
            select(ForecastSystemORM)
            .where(ForecastSystemORM.contract_id == contract_id)
            .options(
                selectinload(ForecastSystemORM.contract),
                selectinload(ForecastSystemORM.port),
                selectinload(ForecastSystemORM.hindcast_point),
                selectinload(ForecastSystemORM.forecast_zones)
            )
        )
        result = await self.session.execute(stmt)
        system_orm = result.scalar_one_or_none() # Usa scalar_one_or_none para la relación UNIQUE
        return orm_to_domain(system_orm) if system_orm else None