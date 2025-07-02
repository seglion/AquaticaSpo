from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, Table
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.shared.base import Base  # Asegúrate de tener tu Base aquí importada
from app.forecastSystems.infrastructure.models import ForecastSystemORM
from app.contracts.domain.models import Contract
from datetime import date
from sqlalchemy import Date  # para mapped_column


contract_user_association = Table(
    "user_contracts",  # nombre real de la tabla
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("contract_id", ForeignKey("contracts.id", ondelete="CASCADE"), primary_key=True)
)

class ContractORM(Base):
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    forecast_system_id: Mapped[int] = mapped_column(ForeignKey("forecast_systems.id"), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)  # Aquí cambia Date por date en el tipo
    end_date: Mapped[date] = mapped_column(Date, nullable=True)
    active: Mapped[bool] = mapped_column(default=True)

    users: Mapped[list["UserORM"]] = relationship(
        "UserORM",
        secondary=contract_user_association,
        back_populates="contracts",
    lazy="joined"
    )
def orm_to_domain(contract_orm: ContractORM) -> Contract:
    return Contract(
        id=contract_orm.id,
        name=contract_orm.name,
        forecast_system_id=contract_orm.forecast_system_id,
        start_date=contract_orm.start_date,
        end_date=contract_orm.end_date,
        active=contract_orm.active,
)

def domain_to_orm(contract: Contract) -> ContractORM:
    return ContractORM(
        name=contract.name,
        forecast_system_id=contract.forecast_system_id,
        start_date=contract.start_date,
        end_date=contract.end_date,
        active=contract.active,
)