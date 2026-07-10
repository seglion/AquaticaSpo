from typing import Optional
from app.forecast_system_results.domain.models import ForecastSystemResult
from app.forecast_system_results.application.repositories import ForecastSystemResultRepositoryABC
from app.forecast_zones.application.repositories import ForecastZoneRepositoryABC # Necesario para la validación de zona
from app.forecastSystems.application.repositories import ForecastSystemRepositoryABC # Para el control de acceso por contrato
from app.users.domain.models import User # Para manejar permisos

class GetLatestForecastSystemResultByZoneUseCase:
    """
    Caso de uso para obtener el resultado de previsión más reciente para una zona específica.

    Control de acceso:
      - Administradores y empleados: cualquier zona.
      - Clientes (resto de usuarios autenticados): solo las zonas cuyos sistemas
        estén ligados a alguno de sus contratos (aislamiento multi-tenant).
    """
    def __init__(
        self,
        result_repo: ForecastSystemResultRepositoryABC,
        zone_repo: ForecastZoneRepositoryABC,
        system_repo: ForecastSystemRepositoryABC,
    ):
        self.result_repo = result_repo
        self.zone_repo = zone_repo
        self.system_repo = system_repo

    async def execute(self, zone_id: int, requester: User) -> Optional[ForecastSystemResult]:
        # 1. La zona debe existir (también hace falta para el control de acceso).
        forecast_zone = await self.zone_repo.get_forecast_zone_by_id(zone_id)
        if not forecast_zone:
            raise ValueError(f"La ForecastZone con ID {zone_id} no existe.")

        # 2. Permisos: admin/empleado ven todo; un cliente solo las zonas de los
        #    sistemas ligados a alguno de sus contratos.
        if not (requester.is_admin or requester.is_employee):
            system = await self.system_repo.getForecastSystemById(forecast_zone.forecast_system_id)
            user_contract_ids = {c.id for c in (requester.contracts or [])}
            if not system or system.contract_id not in user_contract_ids:
                raise PermissionError(
                    "No tienes permiso para ver los resultados de esta zona."
                )

        # 3. Obtener y devolver el resultado más reciente.
        return await self.result_repo.get_latest_result_by_zone(zone_id)
