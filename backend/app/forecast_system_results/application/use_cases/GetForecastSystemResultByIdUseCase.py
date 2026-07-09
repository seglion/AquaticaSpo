from typing import Optional

from app.forecast_system_results.domain.models import ForecastSystemResult
from app.forecast_system_results.application.repositories import ForecastSystemResultRepositoryABC
from app.forecast_zones.application.repositories import ForecastZoneRepositoryABC # Necesario para la validación de zona
from app.users.domain.models import User # Para manejar permisos

class GetForecastSystemResultByIdUseCase:
    """
    Caso de uso para obtener un resultado de previsión por su ID.
    Los administradores pueden ver cualquiera. Los empleados solo pueden ver
    resultados de zonas a las que tienen acceso (requiere lógica de negocio).
    """
    def __init__(self, result_repo: ForecastSystemResultRepositoryABC, zone_repo: ForecastZoneRepositoryABC):
        self.result_repo = result_repo
        self.zone_repo = zone_repo

    async def execute(self, result_id: int, requester: User) -> Optional[ForecastSystemResult]:
        # 1. Obtener el resultado
        result = await self.result_repo.get_forecast_system_result_by_id(result_id)
        if not result:
            return None # El resultado no existe

        # 2. Validación de permisos
        if not requester.is_admin:
            # Lógica de permisos para empleados:
            # Un empleado solo debería ver resultados de zonas a las que tiene acceso.
            # Esto implica que la `ForecastZone` debe estar vinculada a un `ForecastSystem`
            # y el `requester` debe tener un `Contract` con ese `ForecastSystem`.
            # Esta es una lógica de negocio compleja que se implementaría aquí o en un servicio de dominio.
            
            # Placeholder para la lógica de acceso a la zona:
            # Asumimos que `zone_repo` puede verificar el acceso del usuario a la zona.
            # Si `requester.is_employee` y no tiene acceso a `result.forecast_zone_id`:
            # if not await self.zone_repo.check_user_access_to_zone(requester.id, result.forecast_zone_id):
            #     raise PermissionError("No tienes permiso para ver este resultado de previsión.")
            
            # Por ahora, si el usuario no es admin, pero es empleado (permitido por el router),
            # y el resultado existe, se lo permitimos. Adaptar según las reglas de negocio exactas.
            if not requester.is_employee: # Si no es admin ni empleado
                raise PermissionError("No tienes permiso para ver resultados de previsión.")

        return result
