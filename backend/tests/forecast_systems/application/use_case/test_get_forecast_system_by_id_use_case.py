import pytest
from unittest.mock import AsyncMock, MagicMock

from app.forecastSystems.domain.models import ForecastSystem
from app.forecastSystems.application.use_cases.GetForecastSystemByIdUseCase import GetForecastSystemByIdUseCase
from app.forecastSystems.application.repositories import ForecastSystemRepositoryABC
from app.users.domain.models import User

# Fixtures can be reused or redefined if in conftest.py
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
async def test_get_system_by_id_as_admin_found(mock_forecast_system_repo, admin_user):
    """
    Un administrador puede obtener un sistema de previsión por ID si existe.
    """
    # Eliminado 'description'
    existing_system = ForecastSystem(id=1, name="Sistema Existente")
    mock_forecast_system_repo.getForecastSystemById.return_value = existing_system

    use_case = GetForecastSystemByIdUseCase(repo=mock_forecast_system_repo)
    result = await use_case.execute(1, admin_user)

    mock_forecast_system_repo.getForecastSystemById.assert_awaited_once_with(1)
    assert result == existing_system

@pytest.mark.asyncio
async def test_get_system_by_id_as_admin_not_found(mock_forecast_system_repo, admin_user):
    """
    Un administrador recibe None si el sistema no se encuentra.
    """
    mock_forecast_system_repo.getForecastSystemById.return_value = None

    use_case = GetForecastSystemByIdUseCase(repo=mock_forecast_system_repo)
    result = await use_case.execute(999, admin_user) # ID que no existe

    mock_forecast_system_repo.getForecastSystemById.assert_awaited_once_with(999)
    assert result is None

@pytest.mark.asyncio
async def test_get_system_by_id_as_regular_user_fails(mock_forecast_system_repo, regular_user):
    """
    Un usuario regular no puede obtener un sistema de previsión por ID y lanza PermissionError.
    """
    use_case = GetForecastSystemByIdUseCase(repo=mock_forecast_system_repo)

    with pytest.raises(PermissionError) as excinfo:
        await use_case.execute(1, regular_user)

    assert "Solo los administradores pueden consultar sistemas de previsión por ID." in str(excinfo.value)
    mock_forecast_system_repo.getForecastSystemById.assert_not_awaited()