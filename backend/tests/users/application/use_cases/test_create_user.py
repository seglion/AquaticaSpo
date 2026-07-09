import pytest
from app.users.application.use_cases.create_user import CreateUserUseCase
from app.users.domain.models import User

@pytest.mark.asyncio
async def test_create_user_as_admin(mocker):
    mock_repo = mocker.AsyncMock()
    use_case = CreateUserUseCase(mock_repo)

    admin = User(id=1, username="admin", email="a@a.com", hashed_password="123", is_admin=True, is_employee=False)
    new_user = User(id=2, username="test", email="t@t.com", hashed_password="hash", is_admin=False, is_employee=False)

    mock_repo.create_user.return_value = new_user

    result = await use_case.execute(new_user, admin)

    assert result == new_user
    mock_repo.create_user.assert_called_once_with(new_user)

@pytest.mark.asyncio
async def test_create_user_as_non_admin(mocker):
    mock_repo = mocker.AsyncMock()
    use_case = CreateUserUseCase(mock_repo)

    requester = User(id=2, username="test", email="t@t.com", hashed_password="hash", is_admin=False, is_employee=False)
    new_user = User(id=3, username="otro", email="otro@t.com", hashed_password="hash", is_admin=False, is_employee=False) 

    with pytest.raises(PermissionError):
        await use_case.execute(new_user, requester)