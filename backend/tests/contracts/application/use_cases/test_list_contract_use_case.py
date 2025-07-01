import pytest
from unittest.mock import AsyncMock
from datetime import date
from app.contracts.domain.models import Contract
from app.contracts.application.use_cases.ListContractsUseCase import ListContractsUseCase
from app.users.domain.models import User

@pytest.mark.asyncio
async def test_list_contracts_admin_success():
    mock_repo = AsyncMock()
    c1 = Contract(name="Contrato 1", forecast_system_id=1, start_date=date.today())
    c1.id = 1
    c2 = Contract(name="Contrato 2", forecast_system_id=2, start_date=date.today())
    c2.id = 2
    contracts = [c1, c2]
    mock_repo.list_contracts.return_value = contracts

    use_case = ListContractsUseCase(mock_repo)

    admin_user = User(id=1, username="admin", email="admin@test.com", hashed_password="hashed", is_admin=True, is_employee=False)

    result = await use_case.execute(admin_user)

    assert result == contracts
    mock_repo.list_contracts.assert_awaited_once()

@pytest.mark.asyncio
async def test_list_contracts_permission_error():
    mock_repo = AsyncMock()
    use_case = ListContractsUseCase(mock_repo)

    normal_user = User(id=2, username="user", email="user@test.com", hashed_password="hashed", is_admin=False, is_employee=True)

    with pytest.raises(PermissionError):
        await use_case.execute(normal_user)
