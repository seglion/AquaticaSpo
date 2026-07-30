
from dataclasses import dataclass
from datetime import datetime
from typing import Optional,Any


@dataclass
class ForecastSystem:
    """Modelo que representa un sistema de pronóstico."""
    
    name :Optional[str] = None
    contract_id: Optional[int] = None
    port_id: Optional[int] = None
    hindcast_point_id: Optional[int] = None
    id: Optional[int] = None
   

@dataclass
class ForecastZone:
    name: str
    description: Optional[str]
    geom: dict  # Representación de la geometría (GeoJSON como diccionario, por ejemplo)
    dock_elevation: Optional[float] = None  # Cota del dique en metros
    id: Optional[int] = None
    forecast_system_id: Optional[int] = None

@dataclass
class DownloadedData:
    """Modelo que representa una descarga de datos para un punto Hindcast."""
    point_id: int
    downloaded_at: datetime
    data: Any  # JSON almacenado como diccionario
    id: Optional[int] = None  # El ID se asigna al guardarlo en la base de datos