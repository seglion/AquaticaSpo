import pytest
from datetime import date
from unittest.mock import AsyncMock
from app.contracts.domain.models import Contract
from app.contracts.application.use_cases.UpdateContractUseCase import UpdateContractUseCase
from app.users.domain.models import User

@pytest.mark.asyncio
async def test_update_contract_success():
    mock_repo = AsyncMock()
    contract = Contract(name="Contrato actualizado", start_date=date.today(), end_date=None)
    contract.id = 1
    updated_contract = Contract(name="Contrato actualizado", start_date=date.today(), end_date=None)
    updated_contract.id = 1
    mock_repo.update_contract.return_value = updated_contract

    use_case = UpdateContractUseCase(mock_repo)

    admin_user = User(id=1, username="admin", email="admin@test.com", hashed_password="hashed", is_admin=True, is_employee=False)

    result = await use_case.execute(contract, admin_user)

    assert result.id == updated_contract.id
    assert result.name == updated_contract.name
    mock_repo.update_contract.assert_awaited_once_with(contract)

@pytest.mark.asyncio
async def test_update_contract_permission_error():
    mock_repo = AsyncMock()
    use_case = UpdateContractUseCase(mock_repo)

    normal_user = User(id=2, username="user", email="user@test.com", hashed_password="hashed", is_admin=False, is_employee=True)
    contract = Contract(name="Contrato", start_date=date.today(), end_date=None)
    contract.id = 1

    with pytest.raises(PermissionError):
        await use_case.execute(contract, normal_user)
