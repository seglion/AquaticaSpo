from typing import List
from app.contracts.application.repositories import ContractRepositoryABC
from app.users.domain.models import User


class ListUsersByContractIdUseCase:
    def __init__(self, repo: ContractRepositoryABC):
        self.repo = repo

    async def execute(self, contract_id: int, requester: User) -> List[User]:
        if not requester.is_admin:
            raise PermissionError("Solo administradores pueden consultar los usuarios de un contrato.")
        return await self.repo.list_users_by_contract_id(contract_id)
