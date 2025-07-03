# app/forecast_zones/infrastructure/models.py
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func # Para server_default=func.now()

# Importaciones para manejar geometría con PostGIS
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import shape # Necesario para convertir el dict GeoJSON a un objeto Shapely

# Importamos la base declarativa y el modelo de dominio
from app.shared.base import Base # Asume que esta ruta es correcta para tu Base
from app.forecast_zones.domain.models import ForecastZone

# Importa el modelo ORM de ForecastSystem si ya lo tienes definido
# Asegúrate de que esta ruta sea correcta para tu ForecastSystemORM
# Si aún no tienes ForecastSystemORM, tendrás que crearlo, y luego descomentar esta línea.
# from app.forecast_systems.infrastructure.models import ForecastSystemORM 


class ForecastZoneORM(Base):
    """
    Modelo ORM de SQLAlchemy para la tabla 'forecast_zones', utilizando el estilo Mapped.
    """
    __tablename__ = "forecast_zones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Clave foránea a la tabla forecast_systems
    # ondelete="CASCADE" replica el comportamiento que definiste en el DDL
    forecast_system_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("forecast_systems.id", ondelete="CASCADE"), nullable=False
    )
    

    
    # Columna de geometría con PostGIS.
    # Mapped[Geometry] indica que se mapea a un objeto de geometría de geoalchemy2
    geom: Mapped[Geometry] = mapped_column(Geometry(geometry_type='Geometry', srid=4326), nullable=False)

    # Relación con el modelo ForecastSystemORM
    # 'ForecastSystemORM' es una forward reference (cadena de texto) si la clase no está importada
    # type: ignore se usa para suprimir advertencias de Mypy debido a la forward reference.
    # Asegúrate de que ForecastSystemORM tenga un `back_populates="forecast_zones"`
    forecast_system: Mapped["ForecastSystemORM"] = relationship( # type: ignore  # noqa: F821
        "ForecastSystemORM",
        back_populates="forecast_zones"
    )

    def __repr__(self):
        return f"<ForecastZoneORM(id={self.id}, name='{self.name}', forecast_system_id={self.forecast_system_id})>"


def orm_to_domain(orm_obj: ForecastZoneORM) -> ForecastZone:
    """
    Convierte un objeto ForecastZoneORM a un modelo de dominio ForecastZone.
    Maneja la conversión del objeto de geometría de PostGIS/GeoAlchemy2 a un diccionario GeoJSON.
    """
    # Convertir el objeto Geometry de geoalchemy2 a un diccionario GeoJSON
    # to_shape convierte a un objeto Shapely, y .__geo_interface__ lo convierte a GeoJSON dict.
    geom_geojson = to_shape(orm_obj.geom).__geo_interface__ if orm_obj.geom else None

    return ForecastZone(
        id=orm_obj.id,
        name=orm_obj.name,
        description=orm_obj.description,
        forecast_system_id=orm_obj.forecast_system_id,
        geom=geom_geojson, # Pasa el diccionario GeoJSON al modelo de dominio
    )

def domain_to_orm(domain_obj: ForecastZone) -> ForecastZoneORM:
    """
    Convierte un modelo de dominio ForecastZone a un objeto ForecastZoneORM.
    Maneja la conversión del diccionario GeoJSON a un objeto de geometría de GeoAlchemy2.
    """
    # Convertir el diccionario GeoJSON del dominio a un objeto Geometry de geoalchemy2
    # shape() convierte el diccionario GeoJSON a un objeto Shapely, y from_shape() lo convierte a GeoAlchemy2 Geometry.
    geom_alchemy = from_shape(shape(domain_obj.geom)) if domain_obj.geom else None

    orm_obj = ForecastZoneORM(
        name=domain_obj.name,
        description=domain_obj.description,
        forecast_system_id=domain_obj.forecast_system_id,
        geom=geom_alchemy, # Pasa el objeto de geometría de GeoAlchemy2 al ORM
    )
    # Asigna el ID solo si existe, útil para actualizaciones
    if domain_obj.id is not None:
        orm_obj.id = domain_obj.id
    return orm_obj