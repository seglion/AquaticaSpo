# tests/forecast_systems/application/use_cases/test_create_forecast_system_use_case.py
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.forecastSystems.domain.models import ForecastSystem
from app.forecastSystems.application.use_cases.CreateForecastSystemUseCase import CreateForecastSystemUseCase
from app.forecastSystems.application.repositories import ForecastSystemRepositoryABC
from app.users.domain.models import User

@pytest.fixture
def mock_forecast_system_repo():
    """Fixture para mockear el repositorio de ForecastSystem."""
    return AsyncMock(spec=ForecastSystemRepositoryABC)

@pytest.fixture
def admin_user():
    """Fixture para un usuario administrador."""
    user = User(id=1, username="admin", email="admin@example.com", hashed_password="hashed_password", is_admin=True, is_employee=True)
    user.contracts = [] # No necesita contratos para crear system
    return user

@pytest.fixture
def regular_user():
    """Fixture para un usuario regular."""
    user = User(id=2, username="user", email="user@example.com", hashed_password="hashed_password", is_admin=False, is_employee=False)
    user.contracts = []
    return user

@pytest.mark.asyncio
async def test_create_system_as_admin_success(mock_forecast_system_repo, admin_user):
    """
    Un administrador puede crear un sistema de previsión.
    """
    # Se eliminó 'description' de aquí
    new_system_data = ForecastSystem(name="Nuevo Sistema A")
    # Se eliminó 'description' de aquí
    created_system_mock = ForecastSystem(id=1, name="Nuevo Sistema A")

    mock_forecast_system_repo.createForecastSystem.return_value = created_system_mock

    use_case = CreateForecastSystemUseCase(repo=mock_forecast_system_repo)
    result = await use_case.execute(new_system_data, admin_user)

    mock_forecast_system_repo.createForecastSystem.assert_awaited_once_with(new_system_data)
    assert result == created_system_mock
    assert result.id == 1

@pytest.mark.asyncio
async def test_create_system_as_regular_user_fails(mock_forecast_system_repo, regular_user):
    """
    Un usuario regular no puede crear un sistema de previsión y lanza PermissionError.
    """
    # Se eliminó 'description' de aquí
    new_system_data = ForecastSystem(name="Sistema B")

    use_case = CreateForecastSystemUseCase(repo=mock_forecast_system_repo)

    with pytest.raises(PermissionError) as excinfo:
        await use_case.execute(new_system_data, regular_user)

    assert "Solo los administradores pueden crear sistemas de previsión." in str(excinfo.value)
    mock_forecast_system_repo.createForecastSystem.assert_not_awaited() # Asegura que el repo no fue llamado