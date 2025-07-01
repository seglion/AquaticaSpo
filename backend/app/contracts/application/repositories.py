from typing import List, Optional
from app.contracts.domain.models import Contract

class ContractRepositoryABC:
    async def create_contract(self, contract: Contract) -> Contract:
        ...

    async def get_contract_by_id(self, contract_id: int) -> Optional[Contract]:
        ...

    async def list_contracts(self) -> List[Contract]:
        ...

    async def update_contract(self, contract: Contract) -> Contract:
        ...

    async def delete_contract(self, contract_id: int) -> None:
        ...

    async def list_contracts_by_user_id(self, user_id: int) -> List[Contract]:
        ...