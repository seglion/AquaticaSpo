from app.contracts.application.repositories import ContractRepositoryABC
from app.users.application.repositories import UserRepositoryABC  # si tienes repo de usuarios
from app.users.domain.models import User

class AddContractToUserUseCase:
    def __init__(self, contract_repo: ContractRepositoryABC, user_repo: UserRepositoryABC):
        self.contract_repo = contract_repo
        self.user_repo = user_repo

    async def execute(self, contract_id: int, user_id: int, requester: User):
        if not requester.is_admin:
            raise PermissionError("Solo admin puede añadir contratos a usuarios")

        contract = await self.contract_repo.get_contract_by_id(contract_id)
        if not contract:
            raise ValueError("Contrato no encontrado")

        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")

        # Aquí la lógica para añadir el contrato al usuario
        return await self.contract_repo.add_contract_to_user(contract, user)