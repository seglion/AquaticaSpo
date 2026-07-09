# app/forecast_zones/application/use_cases/DeleteForecastZoneUseCase.py
from app.forecast_zones.application.repositories import ForecastZoneRepositoryABC
from app.users.domain.models import User


class DeleteForecastZoneUseCase:
    def __init__(self, repo: ForecastZoneRepositoryABC):
        self.repo = repo

    async def execute(self, zone_id: int, requester: User) -> None:
        """
        Elimina una zona de previsión por su ID.

        Args:
            zone_id: El ID de la zona a eliminar.
            requester: El usuario que realiza la solicitud.
        
        Raises:
            PermissionError: Si el usuario no tiene permisos para eliminar zonas.
            ValueError: Si la zona no se encuentra para eliminar.
        """
        if not requester.is_admin:
            raise PermissionError("Solo los administradores pueden eliminar zonas de previsión.")
        
        # El repositorio devuelve True/False si se eliminó.
        # Aquí decidimos si no se encontró, lanzamos un error.
        deleted = await self.repo.delete_forecast_zone(zone_id)
        if not deleted:
            raise ValueError(f"Zona de previsión con ID {zone_id} no encontrada para eliminar.")