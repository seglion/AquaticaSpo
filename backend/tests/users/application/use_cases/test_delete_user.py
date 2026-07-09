import pytest
from app.users.application.use_cases.delete_user import DeleteUserUseCase
from app.users.domain.models import User

@pytest.mark.asyncio
async def test_delete_user_as_admin(mocker):
    mock_repo = mocker.AsyncMock()
    use_case = DeleteUserUseCase(mock_repo)

    admin = User(id=1, username="admin", email="a@a.com", hashed_password="123", is_admin=True,is_employee=False)

    await use_case.execute(2, admin)

    mock_repo.delete_user.assert_called_once_with(2)

@pytest.mark.asyncio
async def test_delete_user_as_non_admin(mocker):
    mock_repo = mocker.AsyncMock()
    use_case = DeleteUserUseCase(mock_repo)

    requester = User(id=2, username="noadmin", email="t@t.com", hashed_password="123", is_admin=False,is_employee=False)

    with pytest.raises(PermissionError):
        await use_case.execute(3, requester)