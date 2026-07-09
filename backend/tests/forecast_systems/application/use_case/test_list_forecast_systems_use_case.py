import pytest
from unittest.mock import AsyncMock, MagicMock

from app.forecastSystems.domain.models import ForecastSystem
from app.forecastSystems.application.use_cases.ListForecastSystemsUseCase import ListForecastSystemsUseCase
from app.forecastSystems.application.repositories import ForecastSystemRepositoryABC
from app.users.domain.models import User

@pytest.fixture
def mock_forecast_system_repo():
    return AsyncMock(spec=ForecastSystemRepositoryABC)

@pytest.fixture
def admin_user():
    user = User(id=1, username="admin", email="admin@example.com", hashed_password="hashed_password", is_admin=True, is_employee=True)
    user.contracts = []
    return user

@pytest.fixture
def regular_user():
    user = User(id=2, username="user", email="user@example.com", hashed_password="hashed_password", is_admin=False, is_employee=False)
    user.contracts = []
    return user

@pytest.mark.asyncio
async def test_list_systems_as_admin_returns_list(mock_forecast_system_repo, admin_user):
    """
    Un administrador puede listar todos los sistemas de previsión.
    """
    systems_list_mock = [
        ForecastSystem(id=1, name="System A"),
        ForecastSystem(id=2, name="System B")
    ]
    mock_forecast_system_repo.getAllForecastSystems.return_value = systems_list_mock

    use_case = ListForecastSystemsUseCase(repo=mock_forecast_system_repo)
    result = await use_case.execute(admin_user)

    mock_forecast_system_repo.getAllForecastSystems.assert_awaited_once()
    assert result == systems_list_mock
    assert len(result) == 2

@pytest.mark.asyncio
async def test_list_systems_as_admin_returns_empty_list(mock_forecast_system_repo, admin_user):
    """
    Un administrador recibe una lista vacía si no hay sistemas.
    """
    mock_forecast_system_repo.getAllForecastSystems.return_value = []

    use_case = ListForecastSystemsUseCase(repo=mock_forecast_system_repo)
    result = await use_case.execute(admin_user)

    mock_forecast_system_repo.getAllForecastSystems.assert_awaited_once()
    assert result == []

@pytest.mark.asyncio
async def test_list_systems_as_regular_user_fails(mock_forecast_system_repo, regular_user):
    """
    Un usuario regular no puede listar sistemas de previsión y lanza PermissionError.
    """
    use_case = ListForecastSystemsUseCase(repo=mock_forecast_system_repo)

    with pytest.raises(PermissionError) as excinfo:
        await use_case.execute(regular_user)

    assert "Solo los administradores pueden listar sistemas de previsión." in str(excinfo.value)
    mock_forecast_system_repo.getAllForecastSystems.assert_not_awaited()