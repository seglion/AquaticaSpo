from typing import List
from app.contracts.application.repositories import ContractRepositoryABC
from app.contracts.domain.models import Contract
from app.users.domain.models import User

class ListContractsForUserUseCase:
    def __init__(self, repo: ContractRepositoryABC):
        self.repo = repo

    async def execute(self, requester: User) -> List[Contract]:
        if requester.is_admin:
            # Admin puede ver todos, usa el otro caso de uso normal
            return await self.repo.list_contracts()
        return await self.repo.list_contracts_by_user_id(requester.id)