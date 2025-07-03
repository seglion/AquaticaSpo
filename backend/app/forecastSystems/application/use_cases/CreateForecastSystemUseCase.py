# app/forecast_systems/application/use_cases/CreateForecastSystemUseCase.py

from app.forecastSystems.domain.models import ForecastSystem
from app.forecastSystems.application.repositories import ForecastSystemRepositoryABC
from app.users.domain.models import User # Asumiendo que tienes un modelo User en tu dominio

class CreateForecastSystemUseCase:
    """
    Caso de uso para crear un nuevo sistema de previsión.
    """
    def __init__(self, repo: ForecastSystemRepositoryABC):
        self.repo = repo

    async def execute(self, new_system_data: ForecastSystem, requester: User) -> ForecastSystem:
        """
        Ejecuta la creación de un sistema de previsión.

        Args:
            new_system_data (ForecastSystem): Los datos del sistema de previsión a crear.
                                              Su ID debería ser None, ya que será asignado por el repositorio.
            requester (User): El usuario que solicita la creación.

        Returns:
            ForecastSystem: El objeto ForecastSystem creado y persistido, con su ID asignado.

        Raises:
            ValueError: Si el nombre del sistema ya existe.
            PermissionError: Si el usuario no tiene permisos para crear sistemas.
        """
        # --- Restricción 1: Permisos del usuario ---
        # Solo los usuarios administradores deberían poder crear ForecastSystems.
        if not requester.is_admin:
            raise PermissionError("Solo los administradores pueden crear sistemas de previsión.")

    
        # Crear el sistema de previsión a través del repositorio
        created_system = await self.repo.createForecastSystem(new_system_data)
        
        return created_system