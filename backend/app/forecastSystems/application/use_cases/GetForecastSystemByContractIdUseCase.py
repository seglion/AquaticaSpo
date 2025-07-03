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
        self.contract_repo = contract_repo

    async def execute(self, contract_id: int, requester: User) -> Optional[ForecastSystem]:
        """
        Ejecuta la obtención de un sistema de previsión por el ID de un contrato.

        Args:
            contract_id (int): El ID del contrato al que está asociado el sistema de previsión.
            requester (User): El usuario que solicita la consulta.

        Returns:
            Optional[ForecastSystem]: El objeto ForecastSystem si se encuentra y el usuario tiene permisos,
                                      o None si no existe el contrato/sistema, o el usuario no tiene acceso.

        Raises:
            PermissionError: Si el usuario no tiene permisos para acceder a ese contrato/sistema.
            ValueError: Si el contrato no es válido para la consulta (ej. inactivo, fuera de fecha).
        """
        # --- Restricción 1: Permisos del usuario ---

        # 1.1. Los administradores pueden ver cualquier ForecastSystem asociado a cualquier contrato.
        if requester.is_admin:
            # Buscamos el contrato directamente para obtener el forecast_system_id
            contract = await self.contract_repo.get_contract_by_id(contract_id)
            if not contract:
                return None # Contrato no encontrado
            
            # Ahora, obtenemos el ForecastSystem asociado a ese contrato
            return await self.forecast_system_repo.getForecastSystemById(contract.forecast_system_id)


        # 1.2. Para usuarios no administradores: Validar acceso al contrato
        # El usuario DEBE tener este contrato en su lista de contratos
        user_has_contract = False
        target_contract: Optional[Contract] = None

        # Si el objeto User ya carga los contratos asociados, lo usamos.
        # Es vital que 'requester.contracts' sea una lista de objetos Contract, no solo IDs.
        for user_contract in requester.contracts:
            if user_contract.id == contract_id:
                user_has_contract = True
                target_contract = user_contract
                break
        
        if not user_has_contract or target_contract is None:
            raise PermissionError(f"El usuario no tiene acceso al contrato con ID {contract_id}.")

        # --- Restricción 2: El contrato debe estar activo ---
        if not target_contract.active:
            raise ValueError(f"El contrato con ID {contract_id} no está activo.")

        # --- Restricción 3: El contrato debe estar vigente (fechas) ---
        today = date.today()
        if target_contract.start_date > today:
            raise ValueError(f"El contrato con ID {contract_id} aún no ha comenzado.")
        
        if target_contract.end_date and target_contract.end_date < today:
            raise ValueError(f"El contrato con ID {contract_id} ha expirado.")

        # --- Restricción 4: Obtener el ForecastSystem asociado al contrato ---
        # Con todas las validaciones pasadas, ahora obtenemos el ForecastSystem
        # usando el forecast_system_id del contrato.
        if target_contract.forecast_system_id is None:
            # Esto no debería pasar si la FK es NOT NULL en Contract,
            # pero es una buena comprobación de seguridad.
            return None 

        forecast_system = await self.forecast_system_repo.getForecastSystemById(target_contract.forecast_system_id)
        
        return forecast_system
