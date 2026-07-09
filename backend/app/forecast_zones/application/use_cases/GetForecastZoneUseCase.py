# app/forecast_zones/application/use_cases/GetForecastZoneUseCase.py
from typing import Optional
from app.forecast_zones.application.repositories import ForecastZoneRepositoryABC
from app.forecast_zones.domain.models import ForecastZone


class GetForecastZoneUseCase:
    def __init__(self, repo: ForecastZoneRepositoryABC):
        self.repo = repo

    async def execute(self, zone_id: int) -> Optional[ForecastZone]:
        """
        Obtiene una zona de previsión por su ID (sin validación de permisos en esta capa).

        Args:
            zone_id: El ID de la zona a recuperar.
            requester: El usuario que realiza la solicitud (para consistencia, aunque no se usa para permisos aquí).

        Returns:
            La ForecastZone si se encuentra, None en caso contrario.
        """
        zone = await self.repo.get_forecast_zone_by_id(zone_id)
        return zone