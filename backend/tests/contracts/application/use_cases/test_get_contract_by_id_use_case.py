import pytest
from datetime import date
from unittest.mock import AsyncMock
from app.contracts.domain.models import Contract
from app.contracts.application.use_cases.GetContractUseCase import GetContractUseCase
from app.users.domain.models import User

@pytest.mark.asyncio
async def test_get_contract_by_id_success():
    mock_repo = AsyncMock()
    contract = Contract(name="Contrato", forecast_system_id=1, start_date=date.today())
    contract.id = 1
    mock_repo.get_contract_by_id.return_value = contract

    use_case = GetContractUseCase(mock_repo)

    # Creamos un requester que es admin
    admin_user = User(id=1, username="admin", email="admin@test.com", hashed_password="hashed", is_admin=True, is_employee=False)

    result = await use_case.execute(contract_id=1, requester=admin_user)

    assert result.id == 1
    mock_repo.get_contract_by_id.assert_awaited_once_with(1)

@pytest.mark.asyncio
async def test_get_contract_by_id_permission_error():
    mock_repo = AsyncMock()
    use_case = GetContractUseCase(mock_repo)

    # Usuario que no es admin
    normal_user = User(id=2, username="user", email="user@test.com", hashed_password="hashed", is_admin=False, is_employee=True)

    with pytest.raises(PermissionError):
        await use_case.execute(contract_id=1, requester=normal_user)