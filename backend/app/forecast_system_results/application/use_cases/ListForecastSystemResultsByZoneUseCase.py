from typing import List
from app.forecast_system_results.domain.models import ForecastSystemResult
from app.forecast_system_results.application.repositories import ForecastSystemResultRepositoryABC
from app.forecast_zones.application.repositories import ForecastZoneRepositoryABC # Necesario para la validación de zona
from app.users.domain.models import User # Para manejar permisos

class ListForecastSystemResultsByZoneUseCase:
    """
    Caso de uso para listar resultados de previsión para una zona específica.
    Los administradores pueden ver cualquiera. Los empleados solo pueden ver
    resultados de zonas a las que tienen acceso.
    """
    def __init__(self, result_repo: ForecastSystemResultRepositoryABC, zone_repo: ForecastZoneRepositoryABC):
        self.result_repo = result_repo
        self.zone_repo = zone_repo

    async def execute(self, zone_id: int, requester: User, limit: int = 100, offset: int = 0) -> List[ForecastSystemResult]:
        # 1. Validación de permisos
        if not requester.is_admin:
            # Lógica de permisos para empleados (similar a GetByIdUseCase)
            # if not await self.zone_repo.check_user_access_to_zone(requester.id, zone_id):
            #     raise PermissionError("No tienes permiso para listar resultados de esta zona.")
            if not requester.is_employee: # Si no es admin ni empleado
                raise PermissionError("No tienes permiso para listar resultados de previsión.")

        # 2. Validación de la existencia de la zona
        forecast_zone = await self.zone_repo.get_forecast_zone_by_id(zone_id)
        if not forecast_zone:
            raise ValueError(f"La ForecastZone con ID {zone_id} no existe.")

        # 3. Obtener y devolver la lista de resultados
        return await self.result_repo.list_forecast_system_results_by_zone(zone_id, limit, offset)
