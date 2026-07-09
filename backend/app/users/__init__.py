from abc import ABC, abstractmethod
from typing import Optional, List
from app.contracts.domain.models import Contract

class ContractRepositoryABC(ABC):
    @abstractmethod
    async def create_contract(self, contract: Contract) -> Contract:
        ...

    @abstractmethod
    async def get_contract_by_id(self, contract_id: int) -> Optional[Contract]:
        ...

    @abstractmethod
    async def update_contract(self, contract: Contract) -> Contract:
        ...

    @abstractmethod
    async def delete_contract(self, contract_id: int) -> None:
        ...

    @abstractmethod
    async def list_contract(self) -> List[Contract]:
        ...