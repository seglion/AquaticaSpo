
from app.contracts.application.repositories import ContractRepositoryABC
from app.users.domain.models import User  # para el requester

class DeleteContractUseCase:
    def __init__(self, repo: ContractRepositoryABC):
        self.repo = repo

    async def execute(self, contract_id: int, requester: User) -> None:
        if not requester.is_admin:
            raise PermissionError("Solo admin puede borrar contratos")
        
        deleted = await self.repo.delete_contract(contract_id)
        if not deleted:
            raise ValueError("Contrato no encontrado")