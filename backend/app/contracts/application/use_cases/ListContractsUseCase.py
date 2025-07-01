from typing import List
from app.contracts.application.repositories import ContractRepositoryABC
from app.contracts.domain.models import Contract
from app.users.domain.models import User  # para el requester


class ListContractsUseCase:
    def __init__(self, repo: ContractRepositoryABC):
        self.repo = repo

    async def execute(self, requester: User) -> List[Contract]:
        if not requester.is_admin:
            raise PermissionError("Solo admin puede listar contratos")
        return await self.repo.list_contracts()