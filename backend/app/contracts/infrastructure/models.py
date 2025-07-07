from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, Table
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.shared.base import Base  # Asegúrate de tener tu Base aquí importada

from app.contracts.domain.models import Contract
from datetime import date
# from sqlalchemy import Date # No necesitas importar Date si ya importaste datetime.date

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
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=True)
    active: Mapped[bool] = mapped_column(default=True)

    # --- REMOVE THIS LINE IF IT EXISTS AND IS MAPPING forecast_system_id ---
    # forecast_system_id: Mapped[Optional[int]] = mapped_column(ForeignKey("forecast_systems.id"), nullable=True)

    # Relationship for the Many-to-Many with Users
    users: Mapped[list["UserORM"]] = relationship( # type: ignore  # noqa: F821
        "UserORM",
        secondary=contract_user_association,
        back_populates="contracts",
        lazy="joined"
    )

    # --- Add the back-reference for the 1:1 relationship from ForecastSystem ---
    # This allows SQLAlchemy to know about the inverse side of the relationship
    # defined on ForecastSystemORM's 'contract' relationship.
    # uselist=False indicates a one-to-one relationship from this side.
    # Ensure "ForecastSystemORM" refers to the correct class name in its module.
    forecast_system_backref: Mapped[Optional["ForecastSystemORM"]] = relationship(  # noqa: F821
        "ForecastSystemORM",
        back_populates="contract", # This matches the `contract` attribute in ForecastSystemORM
        uselist=False, # Essential for 1:1 relationship from this side
        lazy="joined"
    )


def orm_to_domain(contract_orm: ContractORM) -> Contract:
    if contract_orm is None:
        return None
    return Contract(
        id=contract_orm.id,
        name=contract_orm.name,
        start_date=contract_orm.start_date,
        end_date=contract_orm.end_date,
        active=contract_orm.active
    )

def domain_to_orm(contract: Contract) -> ContractORM:
    # Solo pasar el id si existe, para evitar errores con ContractCreate
    kwargs = dict(
        name=contract.name,
        start_date=contract.start_date,
        end_date=contract.end_date,
        active=contract.active
    )
    if hasattr(contract, "id") and contract.id is not None:
        kwargs["id"] = contract.id
    return ContractORM(**kwargs)