
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.forecastSystems.domain.models import ForecastSystem
from app.forecastSystems.application.use_cases.UpdateForecastSystemUseCase import UpdateForecastSystemUseCase
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
async def test_update_system_as_admin_success(mock_forecast_system_repo, admin_user):
    """
    Un administrador puede actualizar un sistema de previsión existente.
    """
    # Eliminado 'description'
    existing_system = ForecastSystem(id=1, name="Old Name")
    updated_data = ForecastSystem(id=1, name="New Name")

    mock_forecast_system_repo.getForecastSystemById.return_value = existing_system
    mock_forecast_system_repo.updateForecastSystem.return_value = updated_data

    use_case = UpdateForecastSystemUseCase(repo=mock_forecast_system_repo)
    result = await use_case.execute(updated_data, admin_user)

    mock_forecast_system_repo.getForecastSystemById.assert_awaited_once_with(1)
    mock_forecast_system_repo.updateForecastSystem.assert_awaited_once_with(updated_data)
    assert result == updated_data

@pytest.mark.asyncio
async def test_update_system_as_admin_not_found(mock_forecast_system_repo, admin_user):
    """
    Un administrador recibe None si el sistema a actualizar no existe.
    """
    # Eliminado 'description'
    updated_data = ForecastSystem(id=999, name="Non Existent")
    mock_forecast_system_repo.getForecastSystemById.return_value = None # Simula que no se encuentra

    use_case = UpdateForecastSystemUseCase(repo=mock_forecast_system_repo)
    result = await use_case.execute(updated_data, admin_user)

    mock_forecast_system_repo.getForecastSystemById.assert_awaited_once_with(999)
    mock_forecast_system_repo.updateForecastSystem.assert_not_awaited() # No se debe llamar a update
    assert result is None

@pytest.mark.asyncio
async def test_update_system_as_regular_user_fails(mock_forecast_system_repo, regular_user):
    """
    Un usuario regular no puede actualizar un sistema de previsión y lanza PermissionError.
    """
    # Eliminado 'description'
    updated_data = ForecastSystem(id=1, name="New Name")
    use_case = UpdateForecastSystemUseCase(repo=mock_forecast_system_repo)

    with pytest.raises(PermissionError) as excinfo:
        await use_case.execute(updated_data, regular_user)

    assert "Solo los administradores pueden actualizar sistemas de previsión." in str(excinfo.value)
    mock_forecast_system_repo.getForecastSystemById.assert_not_awaited()
    mock_forecast_system_repo.updateForecastSystem.assert_not_awaited()

@pytest.mark.asyncio
async def test_update_system_missing_id_fails(mock_forecast_system_repo, admin_user):
    """
    La actualización falla si los datos no incluyen un ID.
    """
    # Eliminado 'description'
    updated_data = ForecastSystem(name="New Name") # ID is None

    use_case = UpdateForecastSystemUseCase(repo=mock_forecast_system_repo)

    with pytest.raises(ValueError) as excinfo:
        await use_case.execute(updated_data, admin_user)

    assert "El ID del sistema de previsión es necesario para la actualización." in str(excinfo.value)
    mock_forecast_system_repo.getForecastSystemById.assert_not_awaited()
    mock_forecast_system_repo.updateForecastSystem.assert_not_awaited()