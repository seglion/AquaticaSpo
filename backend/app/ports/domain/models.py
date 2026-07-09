# app/ports/domain/models.py
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Port:
    name: str
    country: str
    latitude: float
    longitude: float
    # El ID es generado por la base y se asigna después. No forma parte del constructor.
    id: Optional[int] = field(init=False, default=None)
