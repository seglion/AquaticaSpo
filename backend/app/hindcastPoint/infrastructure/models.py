from sqlalchemy import  String, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.shared.base import Base
from typing import Optional, List
from app.hindcastPoint.domain.models import HindcastPoint

class HindcastPointORM(Base):
    __tablename__ = "hindcast_points"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    models: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

def orm_to_domain(orm_obj: HindcastPointORM) -> HindcastPoint:
    obj = HindcastPoint(
        latitude=orm_obj.latitude,
        longitude=orm_obj.longitude,
        url=orm_obj.url,
        models=orm_obj.models
    )
    obj.id = orm_obj.id
    return obj

def domain_to_orm(domain_obj: HindcastPoint) -> HindcastPointORM:
    orm_obj = HindcastPointORM(
        latitude=domain_obj.latitude,
        longitude=domain_obj.longitude,
        url=domain_obj.url,
        models=domain_obj.models
    )
    if domain_obj.id is not None:
        orm_obj.id = domain_obj.id
    return orm_obj