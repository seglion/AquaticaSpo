from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.users.domain.models import User
from app.users.application.services import UserRepositoryABC
from app.users.infrastructure.models import UserORM, orm_to_domain, domain_to_orm

class UserRepository(UserRepositoryABC):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user: User) -> User:
        user_orm = domain_to_orm(user)
        self.session.add(user_orm)
        await self.session.commit()
        await self.session.refresh(user_orm)
        return orm_to_domain(user_orm)

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        user_orm = await self.session.get(UserORM, user_id)
        return orm_to_domain(user_orm) if user_orm else None

    async def get_user_by_username(self, username: str) -> Optional[User]:
        result = await self.session.execute(
            select(UserORM).where(UserORM.username == username)
        )
        user_orm = result.scalar_one_or_none()
        return orm_to_domain(user_orm) if user_orm else None

    async def update_user(self, user: User) -> User:
        user_orm = await self.session.get(UserORM, user.id)
        if not user_orm:
            raise ValueError("Usuario no encontrado")

        # Actualizamos solo los campos que cambian
        user_orm.username = user.username
        user_orm.email = user.email
        user_orm.hashed_password = user.hashed_password
        user_orm.is_admin = user.is_admin
        user_orm.is_employee = user.is_employee

        self.session.add(user_orm)
        await self.session.commit()
        await self.session.refresh(user_orm)
        return orm_to_domain(user_orm)

    async def delete_user(self, user_id: int) -> None:
        user_orm = await self.session.get(UserORM, user_id)
        if user_orm:
            await self.session.delete(user_orm)
            await self.session.commit()

    async def list_users(self) -> List[User]:
        result = await self.session.execute(select(UserORM))
        users_orm = result.scalars().all()
        return [orm_to_domain(u) for u in users_orm]