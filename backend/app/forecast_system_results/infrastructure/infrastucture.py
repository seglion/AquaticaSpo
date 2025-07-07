# app/forecast_system_results/infrastructure/repositories.py

from typing import List, Optional, Type
from datetime import datetime, timezone
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, NoResultFound, MultipleResultsFound

# Importa el repositorio de dominio (la interfaz que estamos implementando)
from app.forecast_system_results.application.repositories import ForecastSystemResultRepositoryABC as ForecastSystemResultRepository
# Importa el modelo de dominio
from app.forecast_system_results.domain.models import ForecastSystemResult

# Importa el modelo ORM y las funciones de mapeo
from app.forecast_system_results.infrastructure.models import ForecastSystemResultORM, orm_to_domain, domain_to_orm
# Importa ForecastZoneORM si necesitas hacer alguna operación JOIN o validación a través de ella
from app.forecast_zones.infrastructure.models import ForecastZoneORM


class SQLAlchemyForecastSystemResultRepository(ForecastSystemResultRepository):
    """
    Implementación del repositorio de resultados de sistemas de previsión
    que utiliza SQLAlchemy para interactuar con una base de datos PostgreSQL.
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_forecast_system_result(self, result: ForecastSystemResult) -> ForecastSystemResult:
        """
        Crea un nuevo resultado de sistema de previsión en la base de datos.
        """
        orm_result = domain_to_orm(result)
        self._session.add(orm_result)
        try:
            await self._session.flush()  # Obtiene el ID generado por la DB
            await self._session.refresh(orm_result) # Recarga el objeto para asegurar que el ID esté presente
            return orm_to_domain(orm_result)
        except IntegrityError as e:
            await self._session.rollback()
            # Podrías querer manejar errores específicos, por ejemplo, si forecast_zone_id no existe
            raise ValueError(f"No se pudo crear el resultado de previsión debido a un error de integridad: {e}") from e
        except Exception as e:
            await self._session.rollback()
            raise RuntimeError(f"Error inesperado al crear el resultado de previsión: {e}") from e

    async def get_forecast_system_result_by_id(self, result_id: int) -> Optional[ForecastSystemResult]:
        """
        Obtiene un resultado de sistema de previsión por su ID.
        """
        stmt = select(ForecastSystemResultORM).where(ForecastSystemResultORM.id == result_id)
        result = await self._session.execute(stmt)
        orm_result = result.scalar_one_or_none()
        return orm_to_domain(orm_result) if orm_result else None

    async def list_forecast_system_results_by_zone(
        self,
        forecast_zone_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[ForecastSystemResult]:
        """
        Lista los resultados de sistemas de previsión para una zona dada, con paginación.
        """
        # Aquí también podrías cargar la zona para asegurar que exista,
        # pero el caso de uso ya lo hace. Nos enfocamos en la lista de resultados.
        
        stmt = (
            select(ForecastSystemResultORM)
            .where(ForecastSystemResultORM.forecast_zone_id == forecast_zone_id)
            .order_by(desc(ForecastSystemResultORM.execution_date)) # Los más recientes primero
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        orm_results = result.scalars().all()
        return [orm_to_domain(r) for r in orm_results]

    async def get_latest_result_by_zone(self, forecast_zone_id: int) -> Optional[ForecastSystemResult]:
        """
        Obtiene el resultado más reciente para una zona de previsión dada.
        """
        stmt = (
            select(ForecastSystemResultORM)
            .where(ForecastSystemResultORM.forecast_zone_id == forecast_zone_id)
            .order_by(desc(ForecastSystemResultORM.execution_date))
            .limit(1) # Solo queremos uno
        )
        result = await self._session.execute(stmt)
        orm_result = result.scalar_one_or_none()
        return orm_to_domain(orm_result) if orm_result else None

    async def delete_forecast_system_result(self, result_id: int) -> bool:
        """
        Elimina un resultado de sistema de previsión por su ID.
        """
        stmt = select(ForecastSystemResultORM).where(ForecastSystemResultORM.id == result_id)
        result = await self._session.execute(stmt)
        orm_result = result.scalar_one_or_none()

        if orm_result:
            await self._session.delete(orm_result)
            # No necesitamos flush aquí si el commit de la sesión ocurrirá poco después.
            # Pero para asegurar que el cambio se refleje inmediatamente en esta transacción,
            # o para capturar errores de FK antes del commit, un flush es bueno.
            # await self._session.flush()
            return True
        return False