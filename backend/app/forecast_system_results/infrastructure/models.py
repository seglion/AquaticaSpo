from datetime import datetime
from typing import Optional, Any

from sqlalchemy import ForeignKey, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.shared.base import Base
from app.forecast_system_results.domain.models import ForecastSystemResult

# Solo necesitamos importar ForecastZoneORM
from app.forecast_zones.infrastructure.models import ForecastZoneORM


class ForecastSystemResultORM(Base):
    """
    Modelo ORM de SQLAlchemy para la tabla 'forecast_system_results'.
    Un resultado está asociado a una zona específica.
    """
    __tablename__ = "forecast_system_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Clave foránea a la tabla forecast_zones (Many-to-One a ForecastZone)
    forecast_zone_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("forecast_zones.id", ondelete="CASCADE"), nullable=False
    )
    
    # ¡Eliminamos forecast_system_id de aquí!

    execution_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    
    result_data: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Relación: Un resultado pertenece a una zona (Many-to-One)
    # back_populates="forecast_system_results" en ForecastZoneORM
    forecast_zone: Mapped["ForecastZoneORM"] = relationship(
        "ForecastZoneORM",
        back_populates="forecast_system_results",
        lazy="joined"
    )

    # ¡Eliminamos la relación con ForecastSystemORM de aquí!

    def __repr__(self):
        return (f"<ForecastSystemResultORM(id={self.id}, "
                f"forecast_zone_id={self.forecast_zone_id}, "
                f"execution_date={self.execution_date})>")


def orm_to_domain(orm_obj: ForecastSystemResultORM) -> ForecastSystemResult:
    return ForecastSystemResult(
        id=orm_obj.id,
        forecast_zone_id=orm_obj.forecast_zone_id,
        # Eliminamos forecast_system_id del mapeo a dominio
        execution_date=orm_obj.execution_date,
        result_data=orm_obj.result_data
    )

def domain_to_orm(domain_obj: ForecastSystemResult) -> ForecastSystemResultORM:
    orm_obj = ForecastSystemResultORM(
        forecast_zone_id=domain_obj.forecast_zone_id,
        # Eliminamos forecast_system_id del mapeo desde dominio
        execution_date=domain_obj.execution_date,
        result_data=domain_obj.result_data
    )
    if domain_obj.id is not None:
        orm_obj.id = domain_obj.id
    return orm_obj