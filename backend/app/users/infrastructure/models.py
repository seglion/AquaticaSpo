from sqlalchemy import Column, Integer, String, Boolean
from .base import Base
from app.users.domain.models import User

class UserORM(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    is_employee = Column(Boolean, default=False)

def orm_to_domain(user_orm: UserORM) -> User:
    user = User(
        id=user_orm.id,
        username=user_orm.username,
        email=user_orm.email,
        hashed_password=user_orm.hashed_password,
        is_admin=user_orm.is_admin,
        is_employee=user_orm.is_employee,
    )
    return user

def domain_to_orm(user: User) -> UserORM:
    # No seteamos id para que SQLAlchemy gestione el autoincrement
    return UserORM(
        username=user.username,
        email=user.email,
        hashed_password=user.hashed_password,
        is_admin=user.is_admin,
        is_employee=user.is_employee,
    )