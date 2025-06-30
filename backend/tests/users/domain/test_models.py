import pytest
from app.users.domain.models import User

def test_user_creation():
    user = User(
        id=1,
        username="miguel",
        email="miguel@example.com",
        hashed_password="hashedpwd123",
        is_admin=True,
        is_employee=False
    )
    assert user.id == 1
    assert user.username == "miguel"
    assert user.email == "miguel@example.com"
    assert user.hashed_password == "hashedpwd123"
    assert user.is_admin is True
    assert user.is_employee is False