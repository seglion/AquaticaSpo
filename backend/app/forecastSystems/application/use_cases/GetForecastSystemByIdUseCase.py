# app/forecast_systems/application/use_cases/GetForecastSystemByIdUseCase.py

from typing import Optional

from app.forecastSystems.domain.models import ForecastSystem
from app.forecastSystems.application.repositories import ForecastSystemRepositoryABC
from app.users.domain.models import User # Asumiendo que tienes un modelo User en tu dominio

class GetForecastSystemByIdUseCase:
    """
    Caso de uso para obtener un sistema de previsión por su ID.
    """
    def __init__(self, repo: ForecastSystemRepositoryABC):
        self.repo = repo

    async def execute(self, system_id: int, requester: User) -> Optional[ForecastSystem]:
        """
        Ejecuta la obtención de un sistema de previsión por su ID.

        Args:
            system_id (int): El ID único del sistema de previsión a buscar.
            requester (User): El usuario que solicita la consulta.

        Returns:
            Optional[ForecastSystem]: El objeto ForecastSystem si se encuentra, o None si no existe.

        Raises:
            PermissionError: Si el usuario no tiene permisos para obtener sistemas.
        """
        # --- Restricción 1: Permisos del usuario ---
        # Solo los usuarios administradores deberían poder obtener ForecastSystems por ID.
        if not requester.is_admin:
            raise PermissionError("Solo los administradores pueden consultar sistemas de previsión por ID.")

        # Obtener el sistema de previsión a través del repositorio
        forecast_system = await self.repo.getForecastSystemById(system_id)
        
        return forecast_system