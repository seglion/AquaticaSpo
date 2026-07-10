# app/forecast_zones/application/use_cases/ListForecastZonesForSystemUseCase.py
from typing import List
from app.forecast_zones.application.repositories import ForecastZoneRepositoryABC
from app.forecast_zones.domain.models import ForecastZone
from app.forecastSystems.application.repositories import ForecastSystemRepositoryABC  # control de acceso por contrato
from app.users.domain.models import User


class ListForecastZonesForSystemUseCase:
    def __init__(
        self,
        repo: ForecastZoneRepositoryABC,
        system_repo: ForecastSystemRepositoryABC,
    ):
        self.repo = repo
        self.system_repo = system_repo

    async def execute(self, system_id: int, requester: User) -> List[ForecastZone]:
        """
        Lista las zonas de un sistema de previsión.

        Control de acceso: admin y empleados ven cualquier sistema; un cliente solo
        los sistemas ligados a alguno de sus contratos (aislamiento multi-tenant).
        """
        if not (requester.is_admin or requester.is_employee):
            system = await self.system_repo.getForecastSystemById(system_id)
            user_contract_ids = {c.id for c in (requester.contracts or [])}
            if not system or system.contract_id not in user_contract_ids:
                raise PermissionError(
                    "No tienes permiso para ver las zonas de este sistema de previsión."
                )

        zones = await self.repo.list_forecast_zones_by_forecast_system_id(system_id)
        return zones
