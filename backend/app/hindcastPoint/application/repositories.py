from typing import List, Optional
from app.hindcastPoint.domain.models import HindcastPoint
from app.users.domain.models import User

class HindcastPointRepositoryABC:
    async def create_hindcastPoint(self, hindcastpoint: HindcastPoint) -> HindcastPoint:
        ...

    async def get_hindcastPoint_by_id(self, hindcastpoint_id: int) -> Optional[HindcastPoint]:
        ...

    async def list_hindcastPoint(self) -> List[HindcastPoint]:
        ...

    async def update_hindcastPoint(self, hindcastpoint: HindcastPoint) -> HindcastPoint:
        ...

    async def delete_hindcastPoint(self, hindcastpoint_id: int) -> None:
        ...

    