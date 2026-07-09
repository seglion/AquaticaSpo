# app/forecast_zones/application/use_cases/ListForecastZonesUseCase.py
from typing import List
from app.forecast_zones.application.repositories import ForecastZoneRepositoryABC
from app.forecast_zones.domain.models import ForecastZone
from app.users.domain.models import User # Todavía se usa para `requester`, pero su `is_admin` no se verifica aquí.


class ListForecastZonesUseCase:
    def __init__(self, repo: ForecastZoneRepositoryABC):
        self.repo = repo

    async def execute(self, requester: User) -> List[ForecastZone]:
        """
        Lista todas las zonas de previsión (sin validación de permisos en esta capa).

        Args:
            requester: El usuario que realiza la solicitud (para consistencia).

        Returns:
            Una lista de ForecastZone.
        """
        
        if not requester.is_admin:
            raise PermissionError("Solo los administradores pueden crear zonas de previsión.")
        
        
        zones = await self.repo.list_forecast_zones()
        return zones
