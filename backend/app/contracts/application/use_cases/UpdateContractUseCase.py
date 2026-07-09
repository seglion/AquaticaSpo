
from app.contracts.application.repositories import ContractRepositoryABC
from app.contracts.domain.models import Contract
from app.users.domain.models import User  # para el requester

class UpdateContractUseCase:
    def __init__(self, repo: ContractRepositoryABC):
        self.repo = repo

    async def execute(self, contract: Contract, requester: User) -> Contract:
        if not requester.is_admin:
            raise PermissionError("Solo admin puede actualizar contratos")
        return await self.repo.update_contract(contract)