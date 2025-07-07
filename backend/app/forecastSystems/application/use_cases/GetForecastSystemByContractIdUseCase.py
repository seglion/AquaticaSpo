# app/forecast_systems/application/use_cases/GetForecastSystemByContractIdUseCase.py

from typing import Optional
from datetime import date # Necesario para comparar fechas

from app.forecastSystems.domain.models import ForecastSystem
from app.forecastSystems.application.repositories import ForecastSystemRepositoryABC
from app.users.domain.models import User # Ya lo tienes
# ¡Importa el repositorio de contratos! Asumo la ruta:
from app.contracts.application.repositories import ContractRepositoryABC
from app.contracts.domain.models import Contract # Ya lo tienes



class GetForecastSystemByContractIdUseCase:
    """
    Caso de uso para obtener un sistema de previsión asociado a un contrato específico.
    Los administradores pueden acceder a cualquiera. Los usuarios logueados solo a los
    asociados a sus contratos activos.
    """
    def __init__(self, forecast_system_repo: ForecastSystemRepositoryABC, contract_repo: ContractRepositoryABC):
        self.forecast_system_repo = forecast_system_repo
        self.contract_repo = contract_repo # Necesario para validar el contrato si el usuario no es admin

    async def execute(self, contract_id: int, requester: User) -> Optional[ForecastSystem]:
        """
        Ejecuta la obtención de un sistema de previsión por el ID de un contrato.

        Args:
            contract_id (int): El ID del contrato al que está asociado el sistema de previsión.
            requester (User): El usuario que solicita la consulta.

        Returns:
            Optional[ForecastSystem]: El objeto ForecastSystem si se encuentra y el usuario tiene permisos,
                                     o None si no existe el sistema o el usuario no tiene acceso.

        Raises:
            PermissionError: Si el usuario no tiene permisos para acceder a ese contrato/sistema.
            ValueError: Si el contrato no es válido para la consulta (ej. inactivo, fuera de fecha).
        """

        # Primero, buscar el ForecastSystem por el contract_id
        # Asumimos que el repositorio de ForecastSystem tiene un método para esto.
        forecast_system = await self.forecast_system_repo.get_forecast_system_by_contract_id(contract_id)

        if not forecast_system:
            # Si no se encuentra ningún sistema de previsión para este contract_id, no hay nada que devolver.
            return None

        # --- Lógica de permisos y validación de contrato para usuarios no administradores ---
        if not requester.is_admin:
            # 1. El usuario DEBE tener acceso a este contrato.
            user_has_contract = False
            target_contract: Optional[Contract] = None

            # Si el objeto User ya carga los contratos asociados (por ejemplo, a través de una relación Many-to-Many)
            # Asegúrate de que `requester.contracts` sea una lista de objetos `Contract` o al menos contenga los IDs.
            # Aquí asumimos que `requester.contracts` son objetos `Contract` completos con sus propiedades.
            for user_contract in requester.contracts:
                if user_contract.id == contract_id:
                    user_has_contract = True
                    target_contract = user_contract
                    break
            
            if not user_has_contract or target_contract is None:
                # Incluso si el sistema existe, el usuario no tiene el contrato asociado.
                raise PermissionError(f"El usuario no tiene acceso al contrato con ID {contract_id}.")

            # 2. El contrato debe estar activo
            if not target_contract.active:
                raise ValueError(f"El contrato con ID {contract_id} no está activo.")

            # 3. El contrato debe estar vigente (fechas)
            today = date.today()
            if target_contract.start_date > today:
                raise ValueError(f"El contrato con ID {contract_id} aún no ha comenzado.")
            
            if target_contract.end_date and target_contract.end_date < today:
                raise ValueError(f"El contrato con ID {contract_id} ha expirado.")

            # Si todas las validaciones de contrato pasaron, devolvemos el sistema encontrado.
            return forecast_system
        
        # Si es administrador, ya hemos obtenido el sistema al principio y no necesitamos más validaciones de contrato.
        return forecast_system