import pytest
import pytest_asyncio
from unittest.mock import AsyncMock

from app.contracts.application.use_cases.AddContractToUserUseCase import AddContractToUserUseCase
from app.users.domain.models import User
from app.contracts.domain.models import Contract

@pytest_asyncio.fixture
def admin_user():
    return User(id=1, username="admin", email="admin@example.com", hashed_password="hashed", is_admin=True, is_employee=False)

@pytest_asyncio.fixture
def normal_user():
    return User(id=2, username="user", email="user@example.com", hashed_password="hashed", is_admin=False, is_employee=False)

@pytest_asyncio.fixture
def contract():
    return Contract(id=1, name="Contrato1", forecast_system_id=1, start_date="2025-01-01", end_date=None, active=True)

@pytest.mark.asyncio
async def test_add_contract_success(admin_user, contract):
    contract_repo = AsyncMock()
    user_repo = AsyncMock()
    use_case = AddContractToUserUseCase(contract_repo, user_repo)

    contract_repo.get_contract_by_id.return_value = contract
    user_repo.get_user_by_id.return_value = admin_user
    contract_repo.add_contract_to_user.return_value = None

    await use_case.execute(contract.id, admin_user.id, admin_user)

    contract_repo.get_contract_by_id.assert_awaited_once_with(contract.id)
    user_repo.get_user_by_id.assert_awaited_once_with(admin_user.id)
    contract_repo.add_contract_to_user.assert_awaited_once_with(contract, admin_user)

@pytest.mark.asyncio
async def test_add_contract_permission_denied(normal_user):
    contract_repo = AsyncMock()
    user_repo = AsyncMock()
    use_case = AddContractToUserUseCase(contract_repo, user_repo)

    with pytest.raises(PermissionError):
        await use_case.execute(1, 2, normal_user)

@pytest.mark.asyncio
async def test_add_contract_contract_not_found(admin_user):
    contract_repo = AsyncMock()
    user_repo = AsyncMock()
    use_case = AddContractToUserUseCase(contract_repo, user_repo)

    contract_repo.get_contract_by_id.return_value = None
    user_repo.get_user_by_id.return_value = admin_user

    with pytest.raises(ValueError, match="Contrato no encontrado"):
        await use_case.execute(999, admin_user.id, admin_user)

@pytest.mark.asyncio
async def test_add_contract_user_not_found(admin_user, contract):
    contract_repo = AsyncMock()
    user_repo = AsyncMock()
    use_case = AddContractToUserUseCase(contract_repo, user_repo)

    contract_repo.get_contract_by_id.return_value = contract
    user_repo.get_user_by_id.return_value = None

    with pytest.raises(ValueError, match="Usuario no encontrado"):
        await use_case.execute(contract.id, 999, admin_user)