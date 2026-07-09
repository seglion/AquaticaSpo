# app/forecast_systems/domain/models.py
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class ForecastSystem:
    # Campos básicos
    name: str


    # Claves foráneas a otras entidades
    # La relación 1:1 con Contract se modela aquí con un Optional[int]
    contract_id: Optional[int] = None
    
    # La relación 1:1 con Port se modela aquí con un Optional[int]
    port_id: Optional[int] = None 
    
    # La relación 1:1 con HindcastPoint se modela aquí con un Optional[int]
    hindcast_point_id: Optional[int] = None 
    id: Optional[int] = None
    # Para la relación 1:N con ForecastZone, no necesitamos una lista de IDs aquí,
    # ya que la FK está en ForecastZone. El ForecastSystem "tiene" muchas zonas,
    # pero esas zonas lo referencian a él.
    # Si en el futuro necesitaras acceder directamente a ellas desde aquí en el dominio
    # para operaciones de negocio que justifiquen cargar toda la lista,
    # podrías añadirla, pero para el modelo básico, no es necesario.