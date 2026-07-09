# app/forecast_zones/application/use_cases/UpdateForecastZoneUseCase.py
from app.forecast_zones.application.repositories import ForecastZoneRepositoryABC
from app.forecast_zones.domain.models import ForecastZone
from app.users.domain.models import User


class UpdateForecastZoneUseCase:
    def __init__(self, repo: ForecastZoneRepositoryABC):
        self.repo = repo

    async def execute(self, zone_data: ForecastZone, requester: User) -> ForecastZone:
        """
        Actualiza una zona de previsión existente.

        Args:
            zone_data: Los datos actualizados de la zona. Se espera que contenga el ID.
            requester: El usuario que realiza la solicitud.
        
        Returns:
            La ForecastZone actualizada.
        
        Raises:
            PermissionError: Si el usuario no tiene permisos para actualizar la zona.
            ValueError: Si la zona no existe (o el ID no está presente en zone_data).
        """
        if not requester.is_admin:
            raise PermissionError("Solo los administradores pueden actualizar zonas de previsión.")
        
        if zone_data.id is None:
            raise ValueError("ID de zona necesario para la actualización.")
            

        existing_zone = await self.repo.get_forecast_zone_by_id(zone_data.id)
        if not existing_zone:
            raise ValueError(f"Zona de previsión con ID {zone_data.id} no encontrada.")

        updated_zone = await self.repo.update_forecast_zone(zone_data)
        return updated_zone