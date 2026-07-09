# app/forecastSystems/api/schemas.py

from typing import Optional, List
from pydantic import BaseModel, Field

# Importa el modelo de dominio ForecastSystem si necesitas usarlo para validación
# o para derivar automáticamente los esquemas con Config.from_attributes=True
from app.forecastSystems.domain.models import ForecastSystem


# --- Esquemas Base ---

class ForecastSystemBase(BaseModel):
    """
    Esquema base para un Sistema de Previsión.
    Contiene los campos comunes para creación y respuesta.
    """
    name: str = Field(..., example="ECMWF Global Model", description="Nombre único del sistema de previsión.")
    
    # Campos de claves foráneas, opcionales para la creación/actualización directa
    # Pueden ser None si el sistema no está directamente ligado a uno de estos al crearse.
    contract_id: Optional[int] = Field(None, example=1, description="ID del contrato asociado a este sistema de previsión.")
    port_id: Optional[int] = Field(None, example=10, description="ID del puerto principal asociado a este sistema de previsión.")
    hindcast_point_id: Optional[int] = Field(None, example=100, description="ID del punto de hindcast principal asociado a este sistema de previsión.")

    # Configuración para Pydantic.
    # from_attributes = True (anteriormente orm_mode = True) permite que Pydantic
    # lea los datos directamente desde objetos ORM o cualquier objeto con atributos.
    class Config:
        from_attributes = True


# --- Esquemas de Entrada (para Peticiones HTTP) ---

class ForecastSystemCreate(ForecastSystemBase):
    """
    Esquema para crear un nuevo Sistema de Previsión.
    """
    pass


class ForecastSystemUpdate(ForecastSystemBase):
    """
    Esquema para actualizar un Sistema de Previsión existente.
    Todos los campos son opcionales, ya que solo se enviarán los campos que se desean cambiar.
    """
    name: Optional[str] = Field(None, example="ECMWF Global Model Updated", description="Nuevo nombre para el sistema de previsión.")
    

# --- Esquemas de Salida (para Respuestas HTTP) ---

class ForecastSystemResponse(ForecastSystemBase):
    """
    Esquema para la respuesta de un Sistema de Previsión.
    Incluye el ID, que es generado por la base de datos.
    """
    id: int = Field(..., example=1, description="ID único del sistema de previsión.")

    # Puedes añadir aquí campos adicionales para las relaciones,
    # por ejemplo, si quieres incluir una lista de ForecastZoneResponse asociada.
    # Esto requeriría importar ForecastZoneResponse y definir la relación.
    # Ejemplo:
    # from app.forecast_zones.api.schemas import ForecastZoneResponse
    # forecast_zones: List[ForecastZoneResponse] = [] # Se inicializa como lista vacía por defecto
    # Si añades relaciones, asegúrate de que tu ORM las cargue (e.g., lazy="joined" en la relación)
    # y de que tu serialización en la capa de la API las maneje.
