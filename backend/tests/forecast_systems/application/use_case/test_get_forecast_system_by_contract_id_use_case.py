import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import date, timedelta

from app.forecastSystems.domain.models import ForecastSystem
from app.forecastSystems.application.use_cases.GetForecastSystemByContractIdUseCase import GetForecastSystemByContractIdUseCase
from app.forecastSystems.application.repositories import ForecastSystemRepositoryABC
from app.contracts.domain.models import Contract
from app.contracts.application.repositories import ContractRepositoryABC
from app.users.domain.models import User # <-- Ensure this import is present!

# --- Fixtures ---

@pytest.fixture
def mock_forecast_system_repo():
    return AsyncMock(spec=ForecastSystemRepositoryABC)

@pytest.fixture
def mock_contract_repo():
    # The mock will now correctly expect snake_case methods based on your ABC
    return AsyncMock(spec=ContractRepositoryABC)

@pytest.fixture
def admin_user():
    return User(id=1, username="admin", email="admin@example.com", hashed_password="hp", is_admin=True, is_employee=True, contracts=[])

@pytest.fixture
def regular_user_base():
    """
    A base regular user without contracts initially, for creating variants for specific tests.
    """
    return User(id=2, username="user_base", email="user@example.com", hashed_password="hp", is_admin=False, is_employee=False, contracts=[])

@pytest.fixture
def example_forecast_system():
    # Assuming ForecastSystem does not have a 'description' field
    return ForecastSystem(id=1, name="ECMWF System")

@pytest.fixture
def example_contract_active(example_forecast_system):
    return Contract(id=101, name="Active Contract", forecast_system_id=example_forecast_system.id,
                    start_date=date.today() - timedelta(days=5), end_date=date.today() + timedelta(days=5), active=True)

@pytest.fixture
def example_contract_inactive(example_forecast_system):
    return Contract(id=102, name="Inactive Contract", forecast_system_id=example_forecast_system.id,
                    start_date=date.today() - timedelta(days=5), end_date=date.today() + timedelta(days=5), active=False)

@pytest.fixture
def example_contract_not_started(example_forecast_system):
    return Contract(id=103, name="Not Started Contract", forecast_system_id=example_forecast_system.id,
                    start_date=date.today() + timedelta(days=5), end_date=date.today() + timedelta(days=10), active=True)

@pytest.fixture
def example_contract_expired(example_forecast_system):
    return Contract(id=104, name="Expired Contract", forecast_system_id=example_forecast_system.id,
                    start_date=date.today() - timedelta(days=10), end_date=date.today() - timedelta(days=5), active=True)

# --- Tests ---

@pytest.mark.asyncio
async def test_get_system_by_contract_id_as_admin_found(mock_forecast_system_repo, mock_contract_repo, admin_user, example_forecast_system, example_contract_active):
    """
    An administrator can get a forecast system by contract ID if it exists.
    """
    # Using get_contract_by_id (snake_case) to match your implementation
    mock_contract_repo.get_contract_by_id.return_value = example_contract_active
    mock_forecast_system_repo.getForecastSystemById.return_value = example_forecast_system

    use_case = GetForecastSystemByContractIdUseCase(
        forecast_system_repo=mock_forecast_system_repo,
        contract_repo=mock_contract_repo
    )
    result = await use_case.execute(example_contract_active.id, admin_user)

    mock_contract_repo.get_contract_by_id.assert_awaited_once_with(example_contract_active.id)
    mock_forecast_system_repo.getForecastSystemById.assert_awaited_once_with(example_forecast_system.id)
    assert result == example_forecast_system

@pytest.mark.asyncio
async def test_get_system_by_contract_id_as_admin_contract_not_found(mock_forecast_system_repo, mock_contract_repo, admin_user):
    """
    An administrator receives None if the contract is not found.
    """
    mock_contract_repo.get_contract_by_id.return_value = None

    use_case = GetForecastSystemByContractIdUseCase(
        forecast_system_repo=mock_forecast_system_repo,
        contract_repo=mock_contract_repo
    )
    result = await use_case.execute(999, admin_user)

    mock_contract_repo.get_contract_by_id.assert_awaited_once_with(999)
    mock_forecast_system_repo.getForecastSystemById.assert_not_awaited()
    assert result is None

@pytest.mark.asyncio
async def test_get_system_by_contract_id_as_regular_user_with_active_contract(mock_forecast_system_repo, mock_contract_repo, regular_user_base, example_forecast_system, example_contract_active):
    """
    A regular user with an active contract can access the associated forecast system.
    """
    user_with_contract = User(
        id=regular_user_base.id,
        username=regular_user_base.username,
        email=regular_user_base.email,
        hashed_password=regular_user_base.hashed_password,
        is_admin=regular_user_base.is_admin,
        is_employee=regular_user_base.is_employee,
        contracts=[example_contract_active] # Add the specific contract for this test
    )

    mock_forecast_system_repo.getForecastSystemById.return_value = example_forecast_system

    use_case = GetForecastSystemByContractIdUseCase(
        forecast_system_repo=mock_forecast_system_repo,
        contract_repo=mock_contract_repo
    )
    result = await use_case.execute(example_contract_active.id, user_with_contract)

    # For regular users, if the contract is in their list, the contract repo's get_contract_by_id is NOT called.
    mock_contract_repo.get_contract_by_id.assert_not_awaited()
    mock_forecast_system_repo.getForecastSystemById.assert_awaited_once_with(example_forecast_system.id)
    assert result == example_forecast_system

@pytest.mark.asyncio
async def test_get_system_by_contract_id_as_regular_user_without_contract_access_fails(mock_forecast_system_repo, mock_contract_repo, regular_user_base):
    """
    A regular user without access to the associated contract raises a PermissionError.
    """
    user_without_contract = User(
        id=regular_user_base.id,
        username=regular_user_base.username,
        email=regular_user_base.email,
        hashed_password=regular_user_base.hashed_password,
        is_admin=regular_user_base.is_admin,
        is_employee=regular_user_base.is_employee,
        contracts=[] # Empty or not containing the desired contract
    )
    
    use_case = GetForecastSystemByContractIdUseCase(
        forecast_system_repo=mock_forecast_system_repo,
        contract_repo=mock_contract_repo
    )
    
    contract_id_not_owned = 999 

    with pytest.raises(PermissionError) as excinfo:
        await use_case.execute(contract_id_not_owned, user_without_contract)

    assert f"El usuario no tiene acceso al contrato con ID {contract_id_not_owned}." in str(excinfo.value)
    mock_forecast_system_repo.getForecastSystemById.assert_not_awaited()
    mock_contract_repo.get_contract_by_id.assert_not_awaited()

@pytest.mark.asyncio
async def test_get_system_by_contract_id_as_regular_user_contract_inactive_fails(mock_forecast_system_repo, mock_contract_repo, regular_user_base, example_contract_inactive):
    """
    A regular user with an inactive contract raises a ValueError.
    """
    user_with_inactive_contract = User(
        id=regular_user_base.id,
        username=regular_user_base.username,
        email=regular_user_base.email,
        hashed_password=regular_user_base.hashed_password,
        is_admin=regular_user_base.is_admin,
        is_employee=regular_user_base.is_employee,
        contracts=[example_contract_inactive] # Add the inactive contract
    )
    
    use_case = GetForecastSystemByContractIdUseCase(
        forecast_system_repo=mock_forecast_system_repo,
        contract_repo=mock_contract_repo
    )

    with pytest.raises(ValueError) as excinfo:
        await use_case.execute(example_contract_inactive.id, user_with_inactive_contract)

    assert f"El contrato con ID {example_contract_inactive.id} no está activo." in str(excinfo.value)
    mock_forecast_system_repo.getForecastSystemById.assert_not_awaited()
    mock_contract_repo.get_contract_by_id.assert_not_awaited()

@pytest.mark.asyncio
async def test_get_system_by_contract_id_as_regular_user_contract_not_started_fails(mock_forecast_system_repo, mock_contract_repo, regular_user_base, example_contract_not_started):
    """
    A regular user with a contract that has not yet started raises a ValueError.
    """
    user_with_not_started_contract = User(
        id=regular_user_base.id,
        username=regular_user_base.username,
        email=regular_user_base.email,
        hashed_password=regular_user_base.hashed_password,
        is_admin=regular_user_base.is_admin,
        is_employee=regular_user_base.is_employee,
        contracts=[example_contract_not_started]
    )

    use_case = GetForecastSystemByContractIdUseCase(
        forecast_system_repo=mock_forecast_system_repo,
        contract_repo=mock_contract_repo
    )

    with pytest.raises(ValueError) as excinfo:
        await use_case.execute(example_contract_not_started.id, user_with_not_started_contract)

    assert f"El contrato con ID {example_contract_not_started.id} aún no ha comenzado." in str(excinfo.value)
    mock_forecast_system_repo.getForecastSystemById.assert_not_awaited()
    mock_contract_repo.get_contract_by_id.assert_not_awaited()

@pytest.mark.asyncio
async def test_get_system_by_contract_id_as_regular_user_contract_expired_fails(mock_forecast_system_repo, mock_contract_repo, regular_user_base, example_contract_expired):
    """
    A regular user with an expired contract raises a ValueError.
    """
    user_with_expired_contract = User(
        id=regular_user_base.id,
        username=regular_user_base.username,
        email=regular_user_base.email,
        hashed_password=regular_user_base.hashed_password,
        is_admin=regular_user_base.is_admin,
        is_employee=regular_user_base.is_employee,
        contracts=[example_contract_expired]
    )

    use_case = GetForecastSystemByContractIdUseCase(
        forecast_system_repo=mock_forecast_system_repo,
        contract_repo=mock_contract_repo
    )

    with pytest.raises(ValueError) as excinfo:
        await use_case.execute(example_contract_expired.id, user_with_expired_contract)

    assert f"El contrato con ID {example_contract_expired.id} ha expirado." in str(excinfo.value)
    mock_forecast_system_repo.getForecastSystemById.assert_not_awaited()
    mock_contract_repo.get_contract_by_id.assert_not_awaited()

@pytest.mark.asyncio
async def test_get_system_by_contract_id_as_regular_user_contract_fs_id_none_returns_none(mock_forecast_system_repo, mock_contract_repo, regular_user_base):
    """
    If the contract has no forecast_system_id, it should return None.
    """
    contract_without_fs = Contract(id=105, name="Contract No FS", forecast_system_id=None,
                                   start_date=date.today() - timedelta(days=5), end_date=date.today() + timedelta(days=5), active=True)
    user_with_no_fs_contract = User(
        id=regular_user_base.id,
        username=regular_user_base.username,
        email=regular_user_base.email,
        hashed_password=regular_user_base.hashed_password,
        is_admin=regular_user_base.is_admin,
        is_employee=regular_user_base.is_employee,
        contracts=[contract_without_fs]
    )

    use_case = GetForecastSystemByContractIdUseCase(
        forecast_system_repo=mock_forecast_system_repo,
        contract_repo=mock_contract_repo
    )

    result = await use_case.execute(contract_without_fs.id, user_with_no_fs_contract)

    assert result is None
    mock_forecast_system_repo.getForecastSystemById.assert_not_awaited()
    mock_contract_repo.get_contract_by_id.assert_not_awaited()