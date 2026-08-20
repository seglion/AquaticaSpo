from abc import ABC, abstractmethod
from typing import List

from app.users.domain.models import User
from app.notifications.domain.models import (
    ForecastCompletedEvent,
    ForecastFailedEvent,
    Recipient,
)


class NotificationService(ABC):

    @abstractmethod
    async def get_contract_users(self, contract_id: int, requester: User) -> List[Recipient]:
        ...

    @abstractmethod
    async def get_admin_users(self, requester: User) -> List[Recipient]:
        ...

    @abstractmethod
    async def send_completed_email(
        self, recipients: List[Recipient], event: ForecastCompletedEvent, requester: User
    ) -> None:
        ...

    @abstractmethod
    async def send_failed_email(self, recipients: List[Recipient], event: ForecastFailedEvent) -> None:
        ...
