
from dataclasses import dataclass
from typing import Optional


@dataclass
class ForecastSystem:
    """Modelo que representa un sistema de pronóstico."""
    
    hindcast_point_id: Optional[int] = None
    id: Optional[int] = None
   