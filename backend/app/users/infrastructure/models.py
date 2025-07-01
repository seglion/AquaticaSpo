from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, Table, ForeignKey
from app.shared.base import Base  # Asegúrate que sea la misma Base
from app.users.domain.models import User
from app.contracts.infrastructure.models import ContractORM, contract_user_association  # Importa la tabla puente
from app.contracts.domain.models import Contract  # Importa el modelo de dominio Contract


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False)
    is_employee: Mapped[bool] = mapped_column(default=False)

    contracts: Mapped[List["ContractORM"]] = relationship(
        "ContractORM",
        secondary=contract_user_association,
        back_populates="users"
    )

# Mapper auxiliar ContractORM -> Contract (necesario para mapear la lista)
def contract_orm_to_domain(contract_orm: ContractORM) -> Contract:
    return Contract(
        id=contract_orm.id,
        name=contract_orm.name,
        forecast_system_id=contract_orm.forecast_system_id,
        start_date=contract_orm.start_date,
        end_date=contract_orm.end_date,
        active=contract_orm.active,
    )

# Mappers
def orm_to_domain(user_orm: UserORM) -> User:
    return User(
        id=user_orm.id,
        username=user_orm.username,
        email=user_orm.email,
        hashed_password=user_orm.hashed_password,
        is_admin=user_orm.is_admin,
        is_employee=user_orm.is_employee,
        contracts=[contract_orm_to_domain(c) for c in user_orm.contracts] if user_orm.contracts else []
    )

def domain_to_orm(user: User) -> UserORM:
    # Aquí NO incluimos contracts directamente, esa asociación se debe manejar en la infraestructura (repositorio)
    return UserORM(
        username=user.username,
        email=user.email,
        hashed_password=user.hashed_password,
        is_admin=user.is_admin,
        is_employee=user.is_employee,
    )