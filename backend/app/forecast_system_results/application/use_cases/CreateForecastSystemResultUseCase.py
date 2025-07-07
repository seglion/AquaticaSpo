from typing import Any
from datetime import datetime, timezone # Importar timezone para fechas conscientes de zona horaria

from app.forecast_system_results.domain.models import ForecastSystemResult
from app.forecast_system_results.application.repositories import ForecastSystemResultRepositoryABC
from app.forecast_zones.application.repositories import ForecastZoneRepositoryABC # Necesario para validar la zona
from app.users.domain.models import User # Para manejar permisos

class CreateForecastSystemResultUseCase:
    """
    Caso de uso para crear un nuevo resultado de previsión.
    Solo administradores o empleados pueden crear resultados.
    Debe validar que la forecast_zone_id exista.
    """
    def __init__(self, result_repo: ForecastSystemResultRepositoryABC, zone_repo: ForecastZoneRepositoryABC):
        self.result_repo = result_repo
        self.zone_repo = zone_repo

    async def execute(self,
                      forecast_zone_id: int,
                      result_data: Any,
                      requester: User) -> ForecastSystemResult:
        
        # 1. Validación de permisos
        if not (requester.is_admin or requester.is_employee):
            raise PermissionError("Solo los administradores o empleados pueden crear resultados de previsión.")

        # 2. Validación de la existencia de la ForecastZone
        forecast_zone = await self.zone_repo.get_forecast_zone_by_id(forecast_zone_id)
        if not forecast_zone:
            raise ValueError(f"La ForecastZone con ID {forecast_zone_id} no existe.")

        # 3. Creación del objeto de dominio
        # La fecha de ejecución se genera aquí, en la capa de aplicación,
        # ya que es una preocupación de la aplicación (cuándo se procesó el resultado).
        new_result = ForecastSystemResult(
            id=None, # El ID será asignado por la infraestructura (BD)
            forecast_zone_id=forecast_zone_id,
            execution_date=datetime.now(timezone.utc), # Usar UTC para consistencia
            result_data=result_data
        )

        # 4. Persistencia a través del repositorio
        return await self.result_repo.create_forecast_system_result(new_result)
