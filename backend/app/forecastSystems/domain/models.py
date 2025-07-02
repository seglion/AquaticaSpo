from dataclasses import dataclass
from typing import Optional


@dataclass
class ForecastSystem:
    name: str
    id: Optional[int] = None  # Siempre al final