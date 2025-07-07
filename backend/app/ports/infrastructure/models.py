from sqlalchemy import Column, Integer, String, Float
from app.shared.base import Base# pylint: disable=import-error
from app.ports.domain.models import Port
from sqlalchemy.orm import relationship
class PortORM(Base):
    __tablename__ = "ports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    forecast_system_backref = relationship(
        "ForecastSystemORM",
        back_populates="port",
        uselist=False
    )
def orm_to_domain(port_orm: PortORM) -> Port:
    port = Port(
        name=port_orm.name,
        country=port_orm.country,
        latitude=port_orm.latitude,
        longitude=port_orm.longitude,
    )
    port.id = port_orm.id
    return port

def domain_to_orm(port: Port) -> PortORM:
    # NO seteamos el id; SQLAlchemy lo gestiona en INSERT
    return PortORM(
        name=port.name,
        country=port.country,
        latitude=port.latitude,
        longitude=port.longitude,
    )