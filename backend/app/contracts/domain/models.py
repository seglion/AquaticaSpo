# app/ports/domain/models.py
from dataclasses import dataclass, field
from typing import Optional

from datetime import datetime, date


@dataclass
class Contract:
    name: str
    forecast_system_id: int   # Aquí la foreign key hacia sistema de previsión
    start_date: date
    end_date: Optional[date] = None
    active: bool = True
    # El ID es generado por la base y se asigna después. No forma parte del constructor.
    id: Optional[int] = field(init=False, default=None)
