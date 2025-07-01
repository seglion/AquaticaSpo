import pytest
from unittest.mock import AsyncMock
from datetime import date
from app.contracts.domain.models import Contract
from app.contracts.application.use_cases.ListContractsForUserUseCase import ListContractsForUserUseCase
from app.users.domain.models import User

@pytest.mark.asyncio
async def test_list_contracts_for_admin():
    mock_repo = AsyncMock()
    c1 = Contract(name="Contrato 1", forecast_system_id=1, start_date=date.today())
    c1.id = 1
    c2 = Contract(name="Contrato 2", forecast_system_id=2, start_date=date.today())
    c2.id = 2
    contracts = [c1, c2]
    mock_repo.list_contracts.return_value = contracts

    use_case = ListContractsForUserUseCase(mock_repo)

    admin_user = User(id=1, username="admin", email="admin@test.com", hashed_password="hashed", is_admin=True, is_employee=False)

    result = await use_case.execute(admin_user)

    assert result == contracts
    mock_repo.list_contracts.assert_awaited_once()
    mock_repo.list_contracts_by_user_id.assert_not_called()

@pytest.mark.asyncio
async def test_list_contracts_for_normal_user():
    mock_repo = AsyncMock()
    c3 = Contract(name="Contrato 3", forecast_system_id=1, start_date=date.today())
    c3.id = 3
    user_contracts = [c3]
    mock_repo.list_contracts_by_user_id.return_value = user_contracts

    use_case = ListContractsForUserUseCase(mock_repo)

    normal_user = User(id=2, username="user", email="user@test.com", hashed_password="hashed", is_admin=False, is_employee=True)

    result = await use_case.execute(normal_user)

    assert result == user_contracts
    mock_repo.list_contracts_by_user_id.assert_awaited_once_with(normal_user.id)
    mock_repo.list_contracts.assert_not_called()
