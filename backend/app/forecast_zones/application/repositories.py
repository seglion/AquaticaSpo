# app/forecast_zones/application/repositories.py

from typing import List, Optional
from abc import ABC, abstractmethod
from app.forecast_zones.domain.models import ForecastZone


class ForecastZoneRepositoryABC(ABC):
    """
    Define el contrato para los repositorios de ForecastZone.
    """
    @abstractmethod
    async def create_forecast_zone(self, zone: ForecastZone) -> ForecastZone:
        ...
    @abstractmethod
    async def get_forecast_zone_by_id(self, zone_id: int) -> Optional[ForecastZone]:
        ...
    @abstractmethod
    async def list_forecast_zones(self) -> List[ForecastZone]:
        ...
    @abstractmethod
    async def update_forecast_zone(self, zone: ForecastZone) -> ForecastZone:
        ...
    @abstractmethod
    async def delete_forecast_zone(self, zone_id: int) -> bool:
        ...
    @abstractmethod
    async def list_forecast_zones_by_forecast_system_id(self, system_id: int) -> List[ForecastZone]:
        ...