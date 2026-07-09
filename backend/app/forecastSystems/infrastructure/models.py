# app/forecast_systems/infrastructure/models/models.py

from typing import Optional, List

# Core SQLAlchemy imports
from sqlalchemy import Integer, String, ForeignKey # <-- Removed Text as it's no longer used for 'description'
# Mapped and mapped_column for the new SQLAlchemy 2.0 style ORM declarations
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Import your declarative Base
from app.shared.base import Base

# Import your domain model (ForecastSystem)
from app.forecastSystems.domain.models import ForecastSystem

# Import ORM models for relationships.
from app.contracts.infrastructure.models import ContractORM
from app.forecast_zones.infrastructure.models import ForecastZoneORM
from app.ports.infrastructure.models import PortORM # Assuming you have a PortORM
from app.hindcastPoint.infrastructure.models import HindcastPointORM # Assuming you have a HindcastPointORM


class ForecastSystemORM(Base):
    """
    SQLAlchemy ORM model for the 'forecast_systems' table, using Mapped style.
    """
    __tablename__ = "forecast_systems"

    # Primary key, auto-incrementing integer
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # Unique name, cannot be null
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    # --- REMOVED THE DESCRIPTION MAPPING HERE ---
    # description: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # THIS LINE IS GONE NOW

    # --- Foreign Keys ---
    contract_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("contracts.id"), unique=True, nullable=True)
    port_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("ports.id"), unique=True, nullable=True)
    hindcast_point_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("hindcast_points.id"), unique=True, nullable=True)


    # --- Relationships ---
    contract: Mapped[Optional[ContractORM]] = relationship(
        "ContractORM",
        back_populates="forecast_system_backref",
        uselist=False
    )

    port: Mapped[Optional[PortORM]] = relationship(
        "PortORM",
        back_populates="forecast_system_backref",
        uselist=False
    )

    hindcast_point: Mapped[Optional[HindcastPointORM]] = relationship(
        "HindcastPointORM",
        back_populates="forecast_system_backref",
        uselist=False
    )

    forecast_zones: Mapped[List[ForecastZoneORM]] = relationship(
        "ForecastZoneORM",
        back_populates="forecast_system",
        cascade="all, delete-orphan",
        lazy="joined"
    )
    

    def __repr__(self):
        # A helpful representation for debugging - REMOVE description here too
        return (f"<ForecastSystemORM(id={self.id}, name='{self.name}', "
                f"contract_id={self.contract_id}, port_id={self.port_id}, "
                f"hindcast_point_id={self.hindcast_point_id})>") # Description removed from repr


# --- Mappers (assuming these are in the same file or a separate 'mappers.py') ---

def orm_to_domain(forecast_system_orm: ForecastSystemORM) -> ForecastSystem:
    if forecast_system_orm is None:
        return None

    return ForecastSystem(
        id=forecast_system_orm.id,
        name=forecast_system_orm.name,
        # --- REMOVE THIS LINE: description=forecast_system_orm.description, ---
        contract_id=forecast_system_orm.contract_id,
        port_id=forecast_system_orm.port_id,
        hindcast_point_id=forecast_system_orm.hindcast_point_id,
    )

def domain_to_orm(forecast_system: ForecastSystem) -> ForecastSystemORM:
    return ForecastSystemORM(
        name=forecast_system.name,
        # --- REMOVE THIS LINE: description=forecast_system.description, ---
        contract_id=forecast_system.contract_id,
        port_id=forecast_system.port_id,
        hindcast_point_id=forecast_system.hindcast_point_id,
        id=forecast_system.id if forecast_system.id else None
    )