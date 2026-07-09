from app.downloadData.domain.models import DownloadedData
from sqlalchemy import Integer, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.shared.base import Base

from sqlalchemy.sql import func

class DownloadedDataORM(Base):
    __tablename__ = "downloaded_data"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    point_id: Mapped[int] = mapped_column(ForeignKey("hindcast_points.id", ondelete="CASCADE"), nullable=False)
    downloaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    data: Mapped[dict] = mapped_column(JSON, nullable=False)

    hindcast_point: Mapped["HindcastPointORM"] = relationship( # type: ignore  # noqa: F821
    "HindcastPointORM",
    back_populates="downloaded_data"
)
    
def orm_to_domain(orm_obj: DownloadedDataORM) -> DownloadedData:
    obj = DownloadedData(
        id=orm_obj.id,
        point_id=orm_obj.point_id,
        downloaded_at=orm_obj.downloaded_at,
        data=orm_obj.data,
    )
    return obj

def domain_to_orm(domain_obj: DownloadedData) -> DownloadedDataORM:
    orm_obj = DownloadedDataORM(
        point_id=domain_obj.point_id,
        downloaded_at=domain_obj.downloaded_at,
        data=domain_obj.data,
    )
    if domain_obj.id is not None:
        orm_obj.id = domain_obj.id
    return orm_obj