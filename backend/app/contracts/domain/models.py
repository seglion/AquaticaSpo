from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class Contract:
    name: str
    forecast_system_id: int
    start_date: date
    end_date: Optional[date]
    active: bool = True
    id: Optional[int] = None  # Siempre al final