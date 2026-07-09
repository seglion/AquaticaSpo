from typing import List
from app.user.domain.model import User
from abc import ABC, abstractmethod

from app.forecast_systems.domain.models import ForecastSystem


class ForecastService(ABC):
    

    @abstractmethod
    async def get_forecast_systems(self, requester: User) -> List[ForecastSystem]:
        """Método abstracto para obtener sistemas de pronóstico."""
        raise NotImplementedError
    @abstractmethod
    async def download_data_forecast_systems(self,forecast_systems:List[ForecastSystem], requester: User) -> None:
        """Método abstracto para descargar los datos input de los sistemas de pronóstico."""
        raise NotImplementedError