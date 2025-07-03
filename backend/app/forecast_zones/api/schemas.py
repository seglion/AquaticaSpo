# app/forecast_zones/presentation/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ForecastZoneCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    forecast_system_id: int = Field(..., gt=0, description="ID del sistema de previsión al que pertenece esta zona.")
    # Usamos Dict[str, Any] para geom ya que esperamos un objeto GeoJSON genérico
    geom: Dict[str, Any] = Field(..., description="Geometría de la zona en formato GeoJSON (ej. Point, Polygon, MultiPolygon).")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Zona Costera Atlántica",
                "description": "Ejemplo de zona que podría ser un punto o un polígono. Este es un polígono de ejemplo.",
                "forecast_system_id": 2,
                "geom": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-10.0, 42.0],
                            [-9.0, 42.0],
                            [-9.0, 42.5],
                            [-10.0, 42.5],
                            [-10.0, 42.0]
                        ]
                    ]
                }
            },
            # Puedes añadir más ejemplos si los endpoints los soportan o si quieres mostrar variaciones
            "examples": [ # Usar "examples" (en plural) para múltiples ejemplos en OpenAPI 3.1
                {
                    "name": "Zona Punto Faro",
                    "description": "Ejemplo de una zona definida como un punto específico.",
                    "forecast_system_id": 3,
                    "geom": {
                        "type": "Point",
                        "coordinates": [-8.72, 42.24] # Longitud, Latitud para un punto
                    }
                },
                {
                    "name": "Zona Marítima",
                    "description": "Ejemplo de una zona definida como un polígono.",
                    "forecast_system_id": 1,
                    "geom": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [-5.0, 43.0],
                                [-4.0, 43.0],
                                [-4.0, 43.5],
                                [-5.0, 43.5],
                                [-5.0, 43.0]
                            ]
                        ]
                    }
                }
            ]
        }


class ForecastZoneUpdate(ForecastZoneCreate):
    pass

class ForecastZoneResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    forecast_system_id: int
    geom: Dict[str, Any]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Zona Costera Atlántica",
                "description": "Ejemplo de zona que podría ser un punto o un polígono. Este es un polígono de ejemplo.",
                "forecast_system_id": 2,
                "geom": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-10.0, 42.0],
                            [-9.0, 42.0],
                            [-9.0, 42.5],
                            [-10.0, 42.5],
                            [-10.0, 42.0]
                        ]
                    ]
                }
            },
            "examples": [ # Usar "examples" (en plural) para múltiples ejemplos
                 {
                    "id": 4,
                    "name": "Zona Punto Faro",
                    "description": "Ejemplo de una zona definida como un punto específico.",
                    "forecast_system_id": 3,
                    "geom": {
                        "type": "Point",
                        "coordinates": [-8.72, 42.24] # Longitud, Latitud para un punto
                    }
                },
                {
                    "id": 5,
                    "name": "Zona Marítima",
                    "description": "Ejemplo de una zona definida como un polígono.",
                    "forecast_system_id": 1,
                    "geom": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [-5.0, 43.0],
                                [-4.0, 43.0],
                                [-4.0, 43.5],
                                [-5.0, 43.5],
                                [-5.0, 43.0]
                            ]
                        ]
                    }
                }
            ]
        }