from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, Table

from app.shared.base import Base  # Asegúrate de tener tu Base aquí importada

from app.forecastSystems.domain.models import ForecastSystem
from datetime import date
from sqlalchemy import Date  # para mapped_column




class ForecastSystemORM(Base):
    __tablename__ = "forecast_systems"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)


def orm_to_domain(forecastSystem_orm: ForecastSystemORM) -> ForecastSystem:
    forecastSystem = ForecastSystem(
        name=forecastSystem_orm.name,
    )
    forecastSystem_orm.id = forecastSystem_orm.id
    return forecastSystem 

def domain_to_orm(forecastSystem: ForecastSystem) -> ForecastSystemORM:
    # NO seteamos el id; SQLAlchemy lo gestiona en INSERT
    return ForecastSystemORM(
        name=forecastSystem.name,
    )