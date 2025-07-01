from app.contracts.application.repositories import ContractRepositoryABC
from app.contracts.domain.models import Contract
from app.users.domain.models import User  # para el requester

 # para el requester

class CreateContractUseCase:
    def __init__(self, repo: ContractRepositoryABC):
        self.repo = repo

    async def execute(self, contract: Contract, requester: User) -> Contract:
        if not requester.is_admin:
            raise PermissionError("Solo admin puede crear contratos")
        return await self.repo.create_contract(contract)