import pytest
from app.users.application.use_cases.change_password import ChangePasswordUseCase
from app.users.domain.models import User

class FakeUserRepository:
    def __init__(self):
        self.users = {
            1: User(id=1, username="admin", email="admin@example.com", hashed_password="old", is_admin=True, is_employee=False),
            2: User(id=2, username="user", email="user@example.com", hashed_password="old", is_admin=False, is_employee=False)
        }

    async def get_user_by_id(self, user_id):
        return self.users.get(user_id)

    async def update_user(self, user):
        self.users[user.id] = user
        return user

@pytest.mark.asyncio
async def test_admin_can_change_any_password():
    repo = FakeUserRepository()
    use_case = ChangePasswordUseCase(repo)
    requester = repo.users[1]  # admin

    updated_user = await use_case.execute(user_id=2, new_password_hash="new", requester=requester)

    assert updated_user.hashed_password == "new"

@pytest.mark.asyncio
async def test_user_can_change_own_password():
    repo = FakeUserRepository()
    use_case = ChangePasswordUseCase(repo)
    requester = repo.users[2]  # normal user

    updated_user = await use_case.execute(user_id=2, new_password_hash="secure", requester=requester)

    assert updated_user.hashed_password == "secure"

@pytest.mark.asyncio
async def test_user_cannot_change_other_users_password():
    repo = FakeUserRepository()
    use_case = ChangePasswordUseCase(repo)
    requester = repo.users[2]  # normal user

    with pytest.raises(PermissionError):
        await use_case.execute(user_id=1, new_password_hash="hack", requester=requester)
