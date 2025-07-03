# app/forecast_systems/infrastructure/models/models.py

from typing import Optional, List

# Core SQLAlchemy imports
from sqlalchemy import Integer, String, ForeignKey, Text
# Mapped and mapped_column for the new SQLAlchemy 2.0 style ORM declarations
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Import your declarative Base
from app.shared.base import Base 

# Import your domain model
from app.forecastSystems.domain.models import ForecastSystem

# Import ForecastZoneORM for the relationship.
# Using a forward reference ("ForecastZoneORM") is best practice to avoid circular imports,
# especially if ForecastZoneORM also imports ForecastSystemORM.
# We explicitly import it here as a type hint for the relationship,
# but the string literal is what SQLAlchemy uses.
# If you don't use type checkers like MyPy, you could just rely on the string.
from app.forecast_zones.infrastructure.models.models import ForecastZoneORM # Assuming this path and file name


class ForecastSystemORM(Base):
    """
    SQLAlchemy ORM model for the 'forecast_systems' table, using Mapped style.
    """
    __tablename__ = "forecast_systems"

    # Primary key, auto-incrementing integer
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # Unique name, cannot be null
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    # Optional description, using Text for potentially longer strings


    # --- Foreign Keys (Optional, based on your system design) ---
    # If a ForecastSystem is directly linked to these entities, define their FKs here.
    # Marking as Optional[int] and nullable=True allows for systems not linked to these.
    contract_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("contracts.id"), nullable=True)
    port_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("ports.id"), nullable=True)
    hindcast_point_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("hindcast_points.id"), nullable=True)


    # --- Relationships ---
    # One-to-Many relationship with ForecastZoneORM
    # A ForecastSystem can have multiple ForecastZones.
    # The 'ForecastZoneORM' string is a forward reference.
    # 'back_populates' links this relationship to the 'forecast_system' relationship in ForecastZoneORM.
    # 'cascade="all, delete-orphan"' ensures associated ForecastZones are deleted if the system is.
    # 'lazy="joined"' loads related ForecastZones eagerly with the ForecastSystem.
    forecast_zones: Mapped[List[ForecastZoneORM]] = relationship(
        "ForecastZoneORM",
        back_populates="forecast_system",
        cascade="all, delete-orphan",
        lazy="joined"
    )

    def __repr__(self):
        # A helpful representation for debugging
        return (f"<ForecastSystemORM(id={self.id}, name='{self.name}', "
                f"description='{self.description[:20]}...' if self.description else 'None', "
                f"contract_id={self.contract_id}, port_id={self.port_id}, "
                f"hindcast_point_id={self.hindcast_point_id})>")
        
        
        
        
        
        
           
# --- Mapping Functions ---

def orm_to_domain(orm_obj: ForecastSystemORM) -> ForecastSystem:
    """
    Converts a ForecastSystemORM object to a ForecastSystem domain object.
    
    Includes all relevant fields from the ORM model to the domain model.
    """
    return ForecastSystem(
        id=orm_obj.id,  # Map the ID from ORM to domain
        name=orm_obj.name,

        contract_id=orm_obj.contract_id,
        port_id=orm_obj.port_id,
        hindcast_point_id=orm_obj.hindcast_point_id
        # Relationships (like forecast_zones) are typically not mapped directly
        # into the domain model's constructor. Instead, they are handled by
        # the repository or use cases that query for them explicitly.
    )

def domain_to_orm(domain_obj: ForecastSystem) -> ForecastSystemORM:
    """
    Converts a ForecastSystem domain object to a ForecastSystemORM object.
    
    This is primarily for creating new ORM instances from domain objects.
    The ID should generally not be set here, as the database manages it for new records.
    """
    orm_obj = ForecastSystemORM(
        name=domain_obj.name,
        contract_id=domain_obj.contract_id,
        port_id=domain_obj.port_id,
        hindcast_point_id=domain_obj.hindcast_point_id
    )
    # If the domain object already has an ID (e.g., for updates), it can be set.
    # However, for 'create' operations, you generally let the DB assign it.
    if domain_obj.id is not None:
        orm_obj.id = domain_obj.id
    
    return orm_obj