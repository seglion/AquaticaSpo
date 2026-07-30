# app/forecast_zones/domain/models.py
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class ForecastZone:
    name: str
    description: Optional[str]
    forecast_system_id: int
    geom: dict  # Representación de la geometría (GeoJSON como diccionario, por ejemplo)
    dock_elevation: Optional[float] = None  # Cota del dique en metros
    id: Optional[int] = None
