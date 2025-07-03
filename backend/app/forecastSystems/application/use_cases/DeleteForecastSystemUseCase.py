# app/forecast_systems/application/use_cases/DeleteForecastSystemUseCase.py

from app.forecastSystems.application.repositories import ForecastSystemRepositoryABC
from app.users.domain.models import User # Asumiendo que tienes un modelo User en tu dominio

class DeleteForecastSystemUseCase:
    """
    Caso de uso para eliminar un sistema de previsión existente.
    """
    def __init__(self, repo: ForecastSystemRepositoryABC):
        self.repo = repo

    async def execute(self, system_id: int, requester: User) -> bool:
        """
        Ejecuta la eliminación de un sistema de previsión.

        Args:
            system_id (int): El ID único del sistema de previsión a eliminar.
            requester (User): El usuario que solicita la eliminación.

        Returns:
            bool: True si el sistema fue eliminado exitosamente, False si no se encontró.

        Raises:
            PermissionError: Si el usuario no tiene permisos para eliminar sistemas.
        """
        # --- Restricción 1: Permisos del usuario ---
        # Solo los usuarios administradores deberían poder eliminar ForecastSystems.
        if not requester.is_admin:
            raise PermissionError("Solo los administradores pueden eliminar sistemas de previsión.")

        # Eliminar el sistema de previsión a través del repositorio
        # El repositorio devolverá True si se eliminó, False si no se encontró.
        deleted = await self.repo.deleteForecastSystem(system_id)
        
        return deleted