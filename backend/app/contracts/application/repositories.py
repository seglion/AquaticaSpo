from abc import abstractmethod,ABC
from typing import List, Optional
from app.contracts.domain.models import Contract# type: ignore
from app.users.domain.models import User
class ContractRepositoryABC(ABC):
    @abstractmethod
    async def create_contract(self, contract: Contract) -> Contract:# type: ignore
        
        ...
    @abstractmethod
    async def get_contract_by_id(self, contract_id: int) -> Optional[Contract]:# type: ignore
        ...
    @abstractmethod
    async def list_contracts(self) -> List[Contract]:# type: ignore
        ...
    @abstractmethod
    async def update_contract(self, contract: Contract) -> Contract:
        ...
    @abstractmethod
    async def delete_contract(self, contract_id: int) -> None:# type: ignore
        ...
    @abstractmethod
    async def list_contracts_by_user_id(self, user_id: int) -> List[Contract]:
        ...
    @abstractmethod
    async def add_contract_to_user(self, contract: Contract, user: User) -> None:
        ...
    @abstractmethod
    async def remove_contract_from_user(self, contract: Contract, user: User) -> None:
        ...