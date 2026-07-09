

# app/forecast_systems/application/repositories.py

from abc import ABC, abstractmethod  # <-- ¡Importa ABC y abstractmethod!
from typing import List, Optional

from app.forecastSystems.domain.models import ForecastSystem


class ForecastSystemRepositoryABC(ABC):  # <-- ¡Hereda de ABC!
    """
    Clase abstracta base para el repositorio de ForecastSystem.
    Define el contrato que cualquier implementación concreta del repositorio
    (ej. para una base de datos PostgreSQL) debe seguir.
    """

    @abstractmethod  # <-- ¡Añade el decorador!
    async def createForecastSystem(self, forecastSystem: ForecastSystem) -> ForecastSystem:
        """
        Crea un nuevo sistema de previsión en el almacenamiento de datos.
        Debe devolver el objeto ForecastSystem creado con su ID asignado.
        """
        pass  # Usa 'pass' o '...' indistintamente para métodos abstractos

    @abstractmethod  # <-- ¡Añade el decorador!
    async def getForecastSystemById(self, systemId: int) -> Optional[ForecastSystem]:
        """
        Obtiene un sistema de previsión por su ID único.
        Retorna None si el sistema no se encuentra.
        """
        pass

    @abstractmethod  # <-- ¡Añade el decorador!
    async def getAllForecastSystems(self) -> List[ForecastSystem]:
        """
        Obtiene todos los sistemas de previsión disponibles.
        """
        pass

    @abstractmethod  # <-- ¡Añade el decorador!
    async def updateForecastSystem(self, forecastSystem: ForecastSystem) -> Optional[ForecastSystem]:
        """
        Actualiza un sistema de previsión existente.
        Debe devolver el objeto ForecastSystem actualizado.
        Retorna None si el sistema no se encuentra para actualizar.
        """
        pass

    @abstractmethod  # <-- ¡Añade el decorador!
    async def deleteForecastSystem(self, systemId: int) -> bool:
        """
        Elimina un sistema de previsión por su ID.
        Retorna True si el sistema fue eliminado exitosamente, False en caso contrario.
        """
        pass

    @abstractmethod
    async def get_forecast_system_by_contract_id(self, contract_id: int) -> Optional[ForecastSystem]:
        """
        Obtiene un ForecastSystem dado el ID de un contrato.
        Asume que contract_id es UNIQUE en ForecastSystem, o devuelve el primero encontrado.
        """
        pass
