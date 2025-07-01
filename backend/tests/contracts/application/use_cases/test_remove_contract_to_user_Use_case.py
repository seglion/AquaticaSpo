import pytest
from unittest.mock import AsyncMock
from app.contracts.application.use_cases.RemoveContractFromUserUseCase import RemoveContractToUserUseCase
from app.contracts.domain.models import Contract
from app.users.domain.models import User

@pytest.fixture
def contract():
    return Contract(name="Contrato1", forecast_system_id=1, start_date="2025-01-01", end_date=None, active=True)

@pytest.fixture
def user():
    return User(id=1, username="usuario", email="user@example.com", hashed_password="hash", is_admin=False, is_employee=False)

@pytest.fixture
def admin_user():
    return User(id=2, username="admin", email="admin@example.com", hashed_password="hash", is_admin=True, is_employee=False)

@pytest.fixture
def contract_repo(contract):
    repo = AsyncMock()
    repo.get_contract_by_id = AsyncMock(return_value=contract)
    repo.remove_contract_to_user = AsyncMock(return_value=True)
    return repo

@pytest.fixture
def user_repo(user):
    repo = AsyncMock()
    repo.get_user_by_id = AsyncMock(return_value=user)
    return repo

@pytest.mark.asyncio
async def test_remove_contract_success(contract_repo, user_repo, contract, user, admin_user):
    use_case = RemoveContractToUserUseCase(contract_repo, user_repo)
    result = await use_case.execute(contract_id=1, user_id=user.id, requester=admin_user)
    contract_repo.get_contract_by_id.assert_awaited_once_with(1)
    user_repo.get_user_by_id.assert_awaited_once_with(user.id)
    contract_repo.remove_contract_to_user.assert_awaited_once_with(contract, user)
    assert result is True

@pytest.mark.asyncio
async def test_remove_contract_permission_denied(contract_repo, user_repo, contract, user):
    use_case = RemoveContractToUserUseCase(contract_repo, user_repo)
    non_admin = User(id=3, username="notadmin", email="noadmin@example.com", hashed_password="hash", is_admin=False, is_employee=False)
    with pytest.raises(PermissionError) as exc:
        await use_case.execute(contract_id=1, user_id=user.id, requester=non_admin)
    assert str(exc.value) == "Solo admin puede añadir contratos a usuarios"

@pytest.mark.asyncio
async def test_remove_contract_not_found(contract_repo, user_repo, user, admin_user):
    contract_repo.get_contract_by_id = AsyncMock(return_value=None)
    use_case = RemoveContractToUserUseCase(contract_repo, user_repo)
    with pytest.raises(ValueError) as exc:
        await use_case.execute(contract_id=99, user_id=user.id, requester=admin_user)
    assert str(exc.value) == "Contrato no encontrado"

@pytest.mark.asyncio
async def test_remove_user_not_found(contract_repo, user_repo, contract, admin_user):
    user_repo.get_user_by_id = AsyncMock(return_value=None)
    use_case = RemoveContractToUserUseCase(contract_repo, user_repo)
    with pytest.raises(ValueError) as exc:
        await use_case.execute(contract_id=1, user_id=99, requester=admin_user)
    assert str(exc.value) == "Usuario no encontrado"