from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.contracts.domain.models import Contract
from app.users.domain.models import User
from app.contracts.infrastructure.models import ContractORM, orm_to_domain as contract_orm_to_domain, domain_to_orm as domain_to_contract_orm
from app.users.infrastructure.models import UserORM, orm_to_domain as user_orm_to_domain

class ContractRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_contract(self, contract: Contract) -> Contract:
        contract_orm = domain_to_contract_orm(contract)
        self.session.add(contract_orm)
        await self.session.commit()
        await self.session.refresh(contract_orm)
        return contract_orm_to_domain(contract_orm)

    async def get_contract_by_id(self, contract_id: int) -> Optional[Contract]:
        result = await self.session.execute(select(ContractORM).where(ContractORM.id == contract_id))
        contract_orm = result.scalar_one_or_none()
        return contract_orm_to_domain(contract_orm) if contract_orm else None

    async def list_contracts(self) -> List[Contract]:
        result = await self.session.execute(select(ContractORM))
        return [contract_orm_to_domain(c) for c in result.scalars().all()]

    async def update_contract(self, contract: Contract) -> Contract:
        result = await self.session.execute(select(ContractORM).where(ContractORM.id == contract.id))
        contract_orm = result.scalar_one_or_none()
        if not contract_orm:
            raise ValueError("Contrato no encontrado")

        contract_orm.name = contract.name
        contract_orm.forecast_system_id = contract.forecast_system_id
        contract_orm.start_date = contract.start_date
        contract_orm.end_date = contract.end_date
        contract_orm.active = contract.active

        await self.session.commit()
        await self.session.refresh(contract_orm)
        return contract_orm_to_domain(contract_orm)

    async def delete_contract(self, contract_id: int) -> None:
        result = await self.session.execute(select(ContractORM).where(ContractORM.id == contract_id))
        contract_orm = result.scalar_one_or_none()
        if not contract_orm:
            raise ValueError("Contrato no encontrado")

        await self.session.delete(contract_orm)
        await self.session.commit()

    async def list_contracts_by_user_id(self, user_id: int) -> List[Contract]:
        result = await self.session.execute(select(UserORM).where(UserORM.id == user_id))
        user_orm = result.scalar_one_or_none()
        if not user_orm:
            raise ValueError("Usuario no encontrado")

        return [contract_orm_to_domain(c) for c in user_orm.contracts]

    async def add_contract_to_user(self, contract: Contract, user: User) -> None:
        # Carga ORM de ambos
        result_c = await self.session.execute(select(ContractORM).where(ContractORM.id == contract.id))
        contract_orm = result_c.scalar_one_or_none()
        if not contract_orm:
            raise ValueError("Contrato no encontrado")

        result_u = await self.session.execute(select(UserORM).where(UserORM.id == user.id))
        user_orm = result_u.scalar_one_or_none()
        if not user_orm:
            raise ValueError("Usuario no encontrado")

        if contract_orm not in user_orm.contracts:
            user_orm.contracts.append(contract_orm)
            await self.session.commit()

    async def remove_contract_from_user(self, contract: Contract, user: User) -> None:
        result_c = await self.session.execute(select(ContractORM).where(ContractORM.id == contract.id))
        contract_orm = result_c.scalar_one_or_none()
        if not contract_orm:
            raise ValueError("Contrato no encontrado")

        result_u = await self.session.execute(select(UserORM).where(UserORM.id == user.id))
        user_orm = result_u.scalar_one_or_none()
        if not user_orm:
            raise ValueError("Usuario no encontrado")g

        if contract_orm in user_orm.contracts:
            user_orm.contracts.remove(contract_orm)
            await self.session.commit()