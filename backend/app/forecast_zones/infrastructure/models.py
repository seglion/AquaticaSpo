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
from shapely.geometry import Point, Polygon, mapping # Necesitas shapely para convertir el GeoJSON
from geoalchemy2.shape import to_shape # <--- Necesitas esto para convertir el objeto ORM geom a shapely
from shapely.geometry import mapping  # <--- Y esto para convertir el objeto shapely a un diccionario GeoJSON

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
    name: Mapped[str] = mapped_column(String(255),  nullable=False)
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
    obj = ForecastZone(
        id=orm_obj.id,
        name=orm_obj.name,
        description=orm_obj.description,
        forecast_system_id=orm_obj.forecast_system_id,
        # --- CAMBIO CRUCIAL AQUÍ ---
        geom=mapping(to_shape(orm_obj.geom)) if orm_obj.geom else None # Convertir de ORM geom a shapely, luego a GeoJSON dict
    )
    return obj

def domain_to_orm(domain_obj: ForecastZone) -> ForecastZoneORM:
    orm_obj = ForecastZoneORM(
        name=domain_obj.name,
        description=domain_obj.description,
        forecast_system_id=domain_obj.forecast_system_id
    )
    if domain_obj.id is not None:
        orm_obj.id = domain_obj.id
    
    if domain_obj.geom:
        # Convertir el diccionario GeoJSON a un objeto shapely
        # Luego, usar from_shape de geoalchemy2 para obtener la representación ORM
        # ¡Asegúrate de pasar el SRID aquí!
        if domain_obj.geom["type"] == "Point":
            # Si es un punto, las coordenadas son [longitude, latitude]
            shape_obj = Point(domain_obj.geom["coordinates"])
        elif domain_obj.geom["type"] == "Polygon":
            # Si es un polígono, las coordenadas son [[[lon, lat], ...]]
            shape_obj = Polygon(domain_obj.geom["coordinates"][0]) # Asumiendo un solo anillo exterior
        else:
            raise ValueError(f"Tipo de geometría no soportado: {domain_obj.geom['type']}")
            
        # ¡Aquí está la clave! Establece el SRID a 4326
        orm_obj.geom = from_shape(shape_obj, srid=4326) 
    
    return orm_obj