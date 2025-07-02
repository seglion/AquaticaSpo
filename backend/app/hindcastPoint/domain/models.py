# app/ports/domain/models.py
from dataclasses import dataclass, field
from typing import Optional,List

@dataclass
class HindcastPoint:
    """Modelo de un punto de hindcast."""
    latitude: float
    longitude: float
    url: str
    models: Optional[List[str]] = None
    # El ID es generado por la base y se asigna después. No forma parte del constructor.
    id: Optional[int] = field(init=False, default=None)
