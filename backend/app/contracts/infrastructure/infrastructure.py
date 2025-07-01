from typing import List, Optional
from app.contracts.application.repositories import ContractRepositoryABC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.contracts.infrastructure.models import ContractORM, domain_to_orm as contract_domain_to_orm, orm_to_domain as contract_orm_to_domain
from app.users.infrastructure.models import UserORM, orm_to_domain as user_orm_to_domain
from app.contracts.domain.models import Contract
from app.users.domain.models import User

class ContractRepository(ContractRepositoryABC):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_contract(self, contract: Contract) -> Contract:
        contract_orm = contract_domain_to_orm(contract)  # Asumiendo tienes domain_to_orm para contract
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
        contract_orm = await self.session.get(ContractORM, contract.id)
        if not contract_orm:
            raise ValueError("Contrato no encontrado")

        # Actualizar campos (ajusta según tus atributos)
        contract_orm.name = contract.name
        contract_orm.start_date = contract.start_date
        contract_orm.end_date = contract.end_date
        contract_orm.active = contract.active

        await self.session.commit()
        await self.session.refresh(contract_orm)
        return contract_orm_to_domain(contract_orm)

    async def delete_contract(self, contract_id: int) -> None:
        contract_orm = await self.session.get(ContractORM, contract_id)
        if not contract_orm:
            raise ValueError("Contrato no encontrado")

        await self.session.delete(contract_orm)
        await self.session.commit()

    async def list_contracts_by_user_id(self, user_id: int) -> List[Contract]:
        user_orm = await self.session.get(UserORM, user_id)
        if not user_orm:
            return []

        return [contract_orm_to_domain(c) for c in user_orm.contracts]

    async def add_contract_to_user(self, contract: Contract, user: User) -> None:
        contract_orm = await self.session.get(ContractORM, contract.id)
        user_orm = await self.session.get(UserORM, user.id)
        if contract_orm and user_orm:
            if contract_orm not in user_orm.contracts:
                user_orm.contracts.append(contract_orm)
                await self.session.commit()

    async def remove_contract_from_user(self, contract: Contract, user: User) -> None:
        contract_orm = await self.session.get(ContractORM, contract.id)
        user_orm = await self.session.get(UserORM, user.id)
        if contract_orm and user_orm and contract_orm in user_orm.contracts:
            user_orm.contracts.remove(contract_orm)
            await self.session.commit()