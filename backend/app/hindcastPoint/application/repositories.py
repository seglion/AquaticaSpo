from abc import ABC, abstractmethod
from typing import List, Optional
from app.hindcastPoint.domain.models import HindcastPoint
from app.users.domain.models import User

class HindcastPointRepositoryABC(ABC):
    @abstractmethod
    async def create_hindcastPoint(self, hindcastpoint: HindcastPoint) -> HindcastPoint:
        ...
    @abstractmethod

    async def get_hindcastPoint_by_id(self, hindcastpoint_id: int) -> Optional[HindcastPoint]:
        ...
    @abstractmethod
    async def list_hindcastPoint(self) -> List[HindcastPoint]:
        ...
    @abstractmethod
    async def update_hindcastPoint(self, hindcastpoint: HindcastPoint) -> HindcastPoint:
        ...
    @abstractmethod
    async def delete_hindcastPoint(self, hindcastpoint_id: int) -> None:
        ...

    