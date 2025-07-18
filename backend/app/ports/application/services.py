from abc import ABC, abstractmethod
from typing import List, Optional
from app.ports.domain.models import Port

class PortService(ABC):
   
    @abstractmethod
    async def create_port(self, name: str, country: str, latitude: float, longitude: float) -> Port:
        raise NotImplementedError
    @abstractmethod
    async def get_port_by_id(self, port_id: int) ->  Optional[Port]:
        raise NotImplementedError
    @abstractmethod
    async def list_ports(self) -> List[Port]:
        raise NotImplementedError
    @abstractmethod
    async def update_port(self,port_id: int):
        raise NotImplementedError
    @abstractmethod    
    async def delete_port(self,port_id: int) -> bool:
        raise NotImplementedError