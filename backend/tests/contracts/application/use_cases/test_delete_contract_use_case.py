import pytest
from unittest.mock import AsyncMock
from app.contracts.application.use_cases.DeleteContractUseCase import DeleteContractUseCase
from app.users.domain.models import User

@pytest.mark.asyncio
async def test_delete_contract_success():
    mock_repo = AsyncMock()
    mock_repo.delete_contract.return_value = None

    use_case = DeleteContractUseCase(mock_repo)

    admin_user = User(id=1, username="admin", email="admin@test.com", hashed_password="hashed", is_admin=True, is_employee=False)

    await use_case.execute(contract_id=1, requester=admin_user)

    mock_repo.delete_contract.assert_awaited_once_with(1)

@pytest.mark.asyncio
async def test_delete_contract_permission_error():
    mock_repo = AsyncMock()
    use_case = DeleteContractUseCase(mock_repo)

    normal_user = User(id=2, username="user", email="user@test.com", hashed_password="hashed", is_admin=False, is_employee=True)

    with pytest.raises(PermissionError):
        await use_case.execute(contract_id=1, requester=normal_user)