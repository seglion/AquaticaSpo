from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional

from app.users.infrastructure.models import UserORM, orm_to_domain, domain_to_orm
from app.users.domain.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user: User) -> User:
        user_orm = domain_to_orm(user)
        self.session.add(user_orm)
        await self.session.commit()
        await self.session.refresh(user_orm)
        return orm_to_domain(user_orm)

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(select(UserORM).where(UserORM.id == user_id))
        user_orm = result.unique().scalar_one_or_none()
        return orm_to_domain(user_orm) if user_orm else None

    async def get_user_by_username(self, username: str) -> Optional[User]:
        result = await self.session.execute(select(UserORM).where(UserORM.username == username))
        user_orm = result.unique().scalar_one_or_none()
        return orm_to_domain(user_orm) if user_orm else None

    async def list_users(self) -> List[User]:
        result = await self.session.execute(select(UserORM))
        # Solución: usar .unique() antes de scalars().all() para evitar duplicados por joined eager loading
        return [orm_to_domain(user_orm) for user_orm in result.unique().scalars().all()]

    async def update_user(self, user: User) -> Optional[User]:
        result = await self.session.execute(select(UserORM).where(UserORM.id == user.id))
        user_orm = result.unique().scalar_one_or_none()

        if not user_orm:
            return None

        user_orm.username = user.username
        user_orm.email = user.email
        user_orm.hashed_password = user.hashed_password
        user_orm.is_admin = user.is_admin
        user_orm.is_employee = user.is_employee

        await self.session.commit()
        await self.session.refresh(user_orm)
        return orm_to_domain(user_orm)

    async def delete_user(self, user_id: int) -> bool:
        result = await self.session.execute(select(UserORM).where(UserORM.id == user_id))
        user_orm = result.unique().scalar_one_or_none()
        if not user_orm:
            return False

        await self.session.delete(user_orm)
        await self.session.commit()
        return True