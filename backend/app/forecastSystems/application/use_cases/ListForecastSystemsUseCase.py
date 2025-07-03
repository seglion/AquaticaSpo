# app/forecast_systems/application/use_cases/ListForecastSystemsUseCase.py

from typing import List

from app.forecastSystems.domain.models import ForecastSystem
from app.forecastSystems.application.repositories import ForecastSystemRepositoryABC
from app.users.domain.models import User # Asumiendo que tienes un modelo User en tu dominio

class ListForecastSystemsUseCase:
    """
    Caso de uso para listar todos los sistemas de previsión.
    """
    def __init__(self, repo: ForecastSystemRepositoryABC):
        self.repo = repo

    async def execute(self, requester: User) -> List[ForecastSystem]:
        """
        Ejecuta la obtención de la lista de todos los sistemas de previsión.

        Args:
            requester (User): El usuario que solicita la consulta.

        Returns:
            List[ForecastSystem]: Una lista de objetos ForecastSystem. Puede estar vacía si no hay sistemas.

        Raises:
            PermissionError: Si el usuario no tiene permisos para listar sistemas.
        """
        # --- Restricción 1: Permisos del usuario ---
        # Solo los usuarios administradores deberían poder listar todos los ForecastSystems.
        if not requester.is_admin:
            raise PermissionError("Solo los administradores pueden listar sistemas de previsión.")

        # Obtener todos los sistemas de previsión a través del repositorio
        forecast_systems = await self.repo.getAllForecastSystems()
        
        return forecast_systems