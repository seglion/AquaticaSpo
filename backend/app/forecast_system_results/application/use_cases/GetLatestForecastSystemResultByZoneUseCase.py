from typing import Optional
from app.forecast_system_results.domain.models import ForecastSystemResult
from app.forecast_system_results.application.repositories import ForecastSystemResultRepositoryABC
from app.forecast_zones.application.repositories import ForecastZoneRepositoryABC # Necesario para la validación de zona
from app.users.domain.models import User # Para manejar permisos

class GetLatestForecastSystemResultByZoneUseCase:
    """
    Caso de uso para obtener el resultado de previsión más reciente para una zona específica.
    Permisos similares a los otros casos de uso de lectura.
    """
    def __init__(self, result_repo: ForecastSystemResultRepositoryABC, zone_repo: ForecastZoneRepositoryABC):
        self.result_repo = result_repo
        self.zone_repo = zone_repo

    async def execute(self, zone_id: int, requester: User) -> Optional[ForecastSystemResult]:
        # 1. Validación de permisos
        if not requester.is_admin:
            # Lógica de permisos para empleados (similar a los otros casos de uso de lectura)
            # if not await self.zone_repo.check_user_access_to_zone(requester.id, zone_id):
            #     raise PermissionError("No tienes permiso para ver el último resultado de esta zona.")
            if not requester.is_employee: # Si no es admin ni empleado
                raise PermissionError("No tienes permiso para ver el último resultado de previsión.")

        # 2. Validación de la existencia de la zona
        forecast_zone = await self.zone_repo.get_forecast_zone_by_id(zone_id)
        if not forecast_zone:
            raise ValueError(f"La ForecastZone con ID {zone_id} no existe.")

        # 3. Obtener y devolver el resultado más reciente
        return await self.result_repo.get_latest_result_by_zone(zone_id)