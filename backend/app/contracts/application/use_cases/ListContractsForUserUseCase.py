from typing import List
from app.contracts.application.repositories import ContractRepositoryABC
from app.contracts.domain.models import Contract
from app.users.domain.models import User

class ListContractsForUserUseCase:
    def __init__(self, repo: ContractRepositoryABC):
        self.repo = repo

    async def execute(self, requester: User) -> List[Contract]:
        if requester.is_admin:
            # El admin puede ver todos los contratos
            return await self.repo.list_contracts()
        else:
            # Usuario normal solo ve sus contratos asociados
            return await self.repo.list_contracts_by_user_id(requester.id)