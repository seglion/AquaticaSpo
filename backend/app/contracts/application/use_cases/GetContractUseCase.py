from typing import Optional
from app.contracts.application.repositories import ContractRepositoryABC
from app.contracts.domain.models import Contract
from app.users.domain.models import User


class GetContractUseCase:
    def __init__(self, repo: ContractRepositoryABC):
        self.repo = repo

    async def execute(self, contract_id: int, requester: User) -> Optional[Contract]:
        if not requester.is_admin:
            raise PermissionError("Solo admin puede ver contratos")
        return await self.repo.get_contract_by_id(contract_id)