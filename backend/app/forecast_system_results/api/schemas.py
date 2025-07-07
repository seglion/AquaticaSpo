# app/forecast_system_results/presentation/schemas.py

from pydantic import BaseModel, Field, conint
from datetime import datetime
from typing import Dict, Any, List, Optional

# Esquema para la entrada (request body) al crear un resultado de previsión
class ForecastSystemResultCreate(BaseModel):
    forecast_zone_id: int = Field(..., description="ID de la zona de previsión a la que pertenece el resultado.")
    result_data: Dict[str, Any] = Field(..., description="Datos del resultado de la previsión (ej. {'Hs': 2.5, 'Tp': 7.0}).")

    class Config:
        json_schema_extra = {
            "example": {
                "forecast_zone_id": 101,
                "result_data": {
                    "Hs": 2.5,
                    "Tp": 7.0,
                    "PeakDirection": 120
                }
            }
        }

# Esquema para la salida (response) de un resultado de previsión
class ForecastSystemResultResponse(BaseModel):
    id: int = Field(..., description="ID único del resultado de previsión.")
    forecast_zone_id: int = Field(..., description="ID de la zona de previsión asociada.")
    execution_date: datetime = Field(..., description="Fecha y hora de ejecución de la previsión.")
    result_data: Dict[str, Any] = Field(..., description="Datos de la previsión.")

    class Config:
        from_attributes = True # Permite que Pydantic cree una instancia a partir de un ORM u objeto arbitrario
        json_schema_extra = {
            "example": {
                "id": 1,
                "forecast_zone_id": 101,
                "execution_date": "2025-07-04T10:30:00Z",
                "result_data": {
                    "Hs": 2.5,
                    "Tp": 7.0,
                    "PeakDirection": 120
                }
            }
        }

# Esquema para la paginación de listas de resultados
class PaginatedForecastSystemResults(BaseModel):
    items: List[ForecastSystemResultResponse] = Field(..., description="Lista de resultados de previsión.")
    limit: int = Field(..., description="Límite de resultados por página.")
    offset: int = Field(..., description="Offset de la paginación.")