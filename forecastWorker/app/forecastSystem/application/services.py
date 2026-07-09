from ast import Dict
from typing import List, Any, Dict
from app.users.domain.models import User
from abc import ABC, abstractmethod
from app.forecastSystem.domain.models import DownloadedData, ForecastSystem
import pandas as pd
import numpy as np
from app.forecastSystem.domain.models import ForecastZone

class ForecastWorkerService(ABC):
    

    @abstractmethod
    async def get_forecast_system(self, forecast_id: int ,requester: User) -> ForecastSystem:
        """Método abstracto para obtener sistemas de pronóstico."""
        raise NotImplementedError
    @abstractmethod
    
    async def get_forecast_zones(self, forecast_id: int ,requester: User) -> List[ForecastZone]:
        """Método abstracto para obtener sistemas de pronóstico."""
        raise NotImplementedError

    @abstractmethod
    async def get_hindcast_data(self, download_data_id: int ,requester: User) -> DownloadedData:
        """Método abstracto para obtener sistemas de pronóstico."""
        raise NotImplementedError
    
    @abstractmethod
    async def calibration_hindcast_data(self, download_data: DownloadedData ,hinccast_point_id: int,requester :User) -> Dict[str, pd.DataFrame]:
        """Método abstracto para obtener sistemas de pronóstico."""
        raise NotImplementedError
    
    @abstractmethod
    def create_hypercube(self, Hsig: List, Tp: List,Dir:List,Nivel:List) -> np.ndarray:
        """Método abstracto para obtener sistemas de pronóstico."""
        raise NotImplementedError
    
    @abstractmethod
    def propagation(self,hindcast:Dict[str, pd.DataFrame], zones:List[ForecastZone], hypercube:np.ndarray) -> Any:
        """Método abstracto para obtener sistemas de pronóstico."""
        raise NotImplementedError