from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

# Importa el modelo de dominio de ForecastSystemResult
from app.forecast_system_results.domain.models import ForecastSystemResult
# Importa el modelo de dominio de User si tus métodos necesitan el contexto del usuario para permisos
from app.users.domain.models import User 


class ForecastSystemResultRepositoryABC(ABC):
    """
    Clase base abstracta para el repositorio de resultados de sistemas de previsión.
    Define la interfaz (los "puertos") que cualquier implementación de repositorio debe seguir.
    Esta interfaz es utilizada por los casos de uso en la capa de aplicación.
    """

    @abstractmethod
    async def create_forecast_system_result(self, result: ForecastSystemResult) -> ForecastSystemResult:
        """
        Crea un nuevo resultado de previsión en el almacenamiento.
        
        Args:
            result (ForecastSystemResult): El objeto de dominio ForecastSystemResult a crear.
        Returns:
            ForecastSystemResult: El objeto de dominio creado, posiblemente con su ID asignado.
        """
        pass

    @abstractmethod
    async def get_forecast_system_result_by_id(self, result_id: int) -> Optional[ForecastSystemResult]:
        """
        Obtiene un resultado de previsión por su ID único.
        
        Args:
            result_id (int): El ID del resultado de previsión a buscar.
        Returns:
            Optional[ForecastSystemResult]: El objeto de dominio si se encuentra, None en caso contrario.
        """
        pass

    @abstractmethod
    async def list_forecast_system_results_by_zone(self, zone_id: int, limit: int = 100, offset: int = 0) -> List[ForecastSystemResult]:
        """
        Lista resultados de previsión para una zona específica, con paginación.
        
        Args:
            zone_id (int): El ID de la zona de previsión.
            limit (int): El número máximo de resultados a devolver.
            offset (int): El número de resultados a saltar.
        Returns:
            List[ForecastSystemResult]: Una lista de objetos de dominio ForecastSystemResult.
        """
        pass
    
    @abstractmethod
    async def get_latest_result_by_zone(self, zone_id: int) -> Optional[ForecastSystemResult]:
        """
        Obtiene el resultado de previsión más reciente para una zona específica.
        
        Args:
            zone_id (int): El ID de la zona de previsión.
        Returns:
            Optional[ForecastSystemResult]: El objeto de dominio más reciente si existe, None en caso contrario.
        """
        pass

    @abstractmethod
    async def delete_forecast_system_result(self, result_id: int) -> bool:
        """
        Elimina un resultado de previsión por su ID.
        
        Args:
            result_id (int): El ID del resultado de previsión a eliminar.
        Returns:
            bool: True si se eliminó correctamente, False si no se encontró o hubo un error.
        """
        pass
