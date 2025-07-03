import pytest
from unittest.mock import AsyncMock, MagicMock

from app.forecastSystems.application.use_cases.DeleteForecastSystemUseCase import DeleteForecastSystemUseCase
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
async def test_delete_system_as_admin_success(mock_forecast_system_repo, admin_user):
    """
    Un administrador puede eliminar un sistema de previsión existente.
    """
    mock_forecast_system_repo.deleteForecastSystem.return_value = True

    use_case = DeleteForecastSystemUseCase(repo=mock_forecast_system_repo)
    result = await use_case.execute(1, admin_user)

    mock_forecast_system_repo.deleteForecastSystem.assert_awaited_once_with(1)
    assert result is True

@pytest.mark.asyncio
async def test_delete_system_as_admin_not_found(mock_forecast_system_repo, admin_user):
    """
    Un administrador recibe False si el sistema a eliminar no existe.
    """
    mock_forecast_system_repo.deleteForecastSystem.return_value = False

    use_case = DeleteForecastSystemUseCase(repo=mock_forecast_system_repo)
    result = await use_case.execute(999, admin_user) # ID que no existe

    mock_forecast_system_repo.deleteForecastSystem.assert_awaited_once_with(999)
    assert result is False

@pytest.mark.asyncio
async def test_delete_system_as_regular_user_fails(mock_forecast_system_repo, regular_user):
    """
    Un usuario regular no puede eliminar un sistema de previsión y lanza PermissionError.
    """
    use_case = DeleteForecastSystemUseCase(repo=mock_forecast_system_repo)

    with pytest.raises(PermissionError) as excinfo:
        await use_case.execute(1, regular_user)

    assert "Solo los administradores pueden eliminar sistemas de previsión." in str(excinfo.value)
    mock_forecast_system_repo.deleteForecastSystem.assert_not_awaited()