import pytest
from unittest.mock import AsyncMock
from datetime import date

from app.contracts.domain.models import Contract
from app.contracts.application.use_cases.CreateContractUseCase import CreateContractUseCase

@pytest.mark.asyncio
async def test_create_contract_success():
    # Arrange
    mock_repo = AsyncMock()
    use_case = CreateContractUseCase(mock_repo)

    contract_input = Contract(
        name="Contrato de prueba",
        forecast_system_id=1,
        start_date=date.today()
    )

    contract_with_id = Contract(
        name=contract_input.name,
        forecast_system_id=contract_input.forecast_system_id,
        start_date=contract_input.start_date
    )
    contract_with_id.id = 1
    mock_repo.create_contract.return_value = contract_with_id

    # Act
    result = await use_case.execute(contract_input, requester=AsyncMock(is_admin=True))

    # Assert
    assert result.id == 1
    assert result.name == contract_input.name
    mock_repo.create_contract.assert_awaited_once_with(contract_input)