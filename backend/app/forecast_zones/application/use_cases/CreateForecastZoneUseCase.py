# app/forecast_zones/application/use_cases/CreateForecastZoneUseCase.py
from app.forecast_zones.application.repositories import ForecastZoneRepositoryABC
from app.forecast_zones.domain.models import ForecastZone
from app.users.domain.models import User # Asumo que el usuario que realiza la acción se pasa aquí


class CreateForecastZoneUseCase:
    def __init__(self, repo: ForecastZoneRepositoryABC):
        self.repo = repo

    async def execute(self, zone_data: ForecastZone, requester: User) -> ForecastZone:
        """
        Crea una nueva zona de previsión.

        Args:
            zone_data: Los datos de la zona a crear (sin ID).
            requester: El usuario que realiza la solicitud.
        
        Returns:
            La ForecastZone creada con su ID asignado.
        
        Raises:
            PermissionError: Si el usuario no tiene permisos para crear zonas.
            ValueError: Si los datos de entrada no son válidos (ej. system_id no existe).
        """
        
        # 1. Comprobar si el usuario tiene permisos para crear zonas.
        if not requester.is_admin: # Asumiendo que solo los admins pueden crear zonas.
            raise PermissionError("Solo los administradores pueden crear zonas de previsión.")
        

        
        # Crea la zona a través del repositorio
        created_zone = await self.repo.create_forecast_zone(zone_data)
        return created_zone