# app/forecast_zones/application/use_cases/ListForecastZonesForSystemUseCase.py
from typing import List
from app.forecast_zones.application.repositories import ForecastZoneRepositoryABC
from app.forecast_zones.domain.models import ForecastZone
from app.users.domain.models import User # Se mantiene para consistencia, aunque no se usa para permisos aquí.


class ListForecastZonesForSystemUseCase:
    def __init__(self, repo: ForecastZoneRepositoryABC):
        self.repo = repo

    async def execute(self, system_id: int, requester: User) -> List[ForecastZone]:
        """
        Lista las zonas de previsión asociadas a un sistema de previsión específico (sin validación de permisos aquí).

        Args:
            system_id: El ID del sistema de previsión.
            requester: El usuario que realiza la solicitud (para consistencia).

        Returns:
            Una lista de ForecastZone asociadas al sistema.
        """
        if not requester.is_admin:
            raise PermissionError("Solo los administradores pueden listar zonas por sistema de prevision .")
        
        
        
        
        zones = await self.repo.list_forecast_zones_by_forecast_system_id(system_id)
        return zones