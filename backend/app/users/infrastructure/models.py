from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, Table, ForeignKey
from app.shared.base import Base
from app.users.domain.models import User
from app.contracts.infrastructure.models import ContractORM, contract_user_association
from app.contracts.domain.models import Contract


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False)
    is_employee: Mapped[bool] = mapped_column(default=False)

    contracts: Mapped[List[ContractORM]] = relationship(
        ContractORM,
        secondary=contract_user_association,
        back_populates="users",lazy="joined"
    )

# Mapper auxiliar ContractORM -> Contract (necesario para mapear la lista)
def contract_orm_to_domain(contract_orm: ContractORM) -> Contract:
    # El dominio Contract ya NO acepta forecast_system_id
    return Contract(
        id=contract_orm.id,
        name=contract_orm.name,
        start_date=contract_orm.start_date,
        end_date=contract_orm.end_date,
        active=contract_orm.active
    )

# Mappers
def orm_to_domain(user_orm: UserORM) -> User:
    print(f"DEBUG: Entering orm_to_domain for User. User ID: {user_orm.id}, Username: {user_orm.username}")

    # Check hashed_password type explicitly
    if not isinstance(user_orm.hashed_password, str):
        print(f"CRITICAL ERROR: user_orm.hashed_password is not a string. Type: {type(user_orm.hashed_password)}, Value: {user_orm.hashed_password}")
        raise TypeError(f"hashed_password is of type {type(user_orm.hashed_password)}, expected str")


    print(f"DEBUG: UserORM.hashed_password type: {type(user_orm.hashed_password)}, value: {user_orm.hashed_password}")
    print(f"DEBUG: UserORM.contracts content (before mapping): {user_orm.contracts}")

    try:
        # This part looks fine as empty list is falsey, and default_factory in dataclass handles empty list properly
        domain_contracts = [contract_orm_to_domain(c) for c in user_orm.contracts] if user_orm.contracts else []
        print(f"DEBUG: Mapped {len(domain_contracts)} contracts for user {user_orm.username}.")
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to map contracts for user {user_orm.username}: {e}")
        raise # Re-raise to get the full traceback

    try:
        domain_user = User(
            id=user_orm.id,
            username=user_orm.username,
            email=user_orm.email,
            hashed_password=user_orm.hashed_password,
            is_admin=user_orm.is_admin,
            is_employee=user_orm.is_employee,
            contracts=domain_contracts
        )
        print(f"DEBUG: Successfully created User domain object for {user_orm.username}")
        return domain_user
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to instantiate User domain model for {user_orm.username}: {e}")
        raise # Re-raise to get the full traceback

def domain_to_orm(user: User) -> UserORM:
    # ... (no changes needed here, as it's for creating/updating ORM)
    return UserORM(
        username=user.username,
        email=user.email,
        hashed_password=user.hashed_password,
        is_admin=user.is_admin,
        is_employee=user.is_employee,
    )
