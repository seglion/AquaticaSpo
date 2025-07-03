# app/forecast_zones/application/repositories.py

from typing import List, Optional

from app.forecast_zones.domain.models import ForecastZone


class ForecastZoneRepositoryABC():
    """
    Define el contrato para los repositorios de ForecastZone.
    """

    async def create_forecast_zone(self, zone: ForecastZone) -> ForecastZone:
        ...

    async def get_forecast_zone_by_id(self, zone_id: int) -> Optional[ForecastZone]:
        ...

    async def list_forecast_zones(self) -> List[ForecastZone]:
        ...

    async def update_forecast_zone(self, zone: ForecastZone) -> ForecastZone:
        ...

    async def delete_forecast_zone(self, zone_id: int) -> bool:
        ...

    async def list_forecast_zones_by_forecast_system_id(self, system_id: int) -> List[ForecastZone]:
        ...