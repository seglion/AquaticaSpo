import pytest
from unittest.mock import AsyncMock
from datetime import datetime, timezone

from app.forecast_system_results.domain.models import ForecastSystemResult
from app.users.domain.models import User
from app.forecast_zones.domain.models import ForecastZone # Necesario para el constructor del UC

from app.forecast_system_results.application.use_cases.GetForecastSystemResultByIdUseCase import GetForecastSystemResultByIdUseCase

@pytest.fixture
def mock_result_repo():
    return AsyncMock()

@pytest.fixture
def mock_zone_repo():
    return AsyncMock()

@pytest.fixture
def admin_user():
    return User(id=1, username="admin", email="admin@example.com", hashed_password="hashed_pass", is_admin=True, is_employee=True)

@pytest.fixture
def employee_user():
    return User(id=2, username="employee", email="employee@example.com", hashed_password="hashed_pass", is_admin=False, is_employee=True)

@pytest.fixture
def client_user():
    return User(id=3, username="client", email="client@example.com", hashed_password="hashed_pass", is_admin=False, is_employee=False)

@pytest.fixture
def sample_result():
    return ForecastSystemResult(
        id=1,
        forecast_zone_id=101,
        execution_date=datetime.now(timezone.utc),
        result_data={"Hs": 2.0}
    )

class TestGetForecastSystemResultByIdUseCase:

    @pytest.mark.asyncio
    async def test_get_result_as_admin_success(self, mock_result_repo, mock_zone_repo, admin_user, sample_result):
        mock_result_repo.get_forecast_system_result_by_id.return_value = sample_result
        
        use_case = GetForecastSystemResultByIdUseCase(mock_result_repo, mock_zone_repo)
        result = await use_case.execute(sample_result.id, admin_user)

        mock_result_repo.get_forecast_system_result_by_id.assert_called_once_with(sample_result.id)
        assert result == sample_result

    @pytest.mark.asyncio
    async def test_get_result_as_employee_success(self, mock_result_repo, mock_zone_repo, employee_user, sample_result):
        mock_result_repo.get_forecast_system_result_by_id.return_value = sample_result
        
        use_case = GetForecastSystemResultByIdUseCase(mock_result_repo, mock_zone_repo)
        result = await use_case.execute(sample_result.id, employee_user)

        mock_result_repo.get_forecast_system_result_by_id.assert_called_once_with(sample_result.id)
        assert result == sample_result

    @pytest.mark.asyncio
    async def test_get_result_permission_denied_for_client(self, mock_result_repo, mock_zone_repo, client_user, sample_result):
        mock_result_repo.get_forecast_system_result_by_id.return_value = sample_result

        use_case = GetForecastSystemResultByIdUseCase(mock_result_repo, mock_zone_repo)

        with pytest.raises(PermissionError, match="No tienes permiso para ver resultados de previsión."):
            await use_case.execute(sample_result.id, client_user)

        mock_result_repo.get_forecast_system_result_by_id.assert_called_once_with(sample_result.id)

    @pytest.mark.asyncio
    async def test_get_result_not_found(self, mock_result_repo, mock_zone_repo, admin_user):
        mock_result_repo.get_forecast_system_result_by_id.return_value = None
        
        use_case = GetForecastSystemResultByIdUseCase(mock_result_repo, mock_zone_repo)
        result = await use_case.execute(999, admin_user)

        mock_result_repo.get_forecast_system_result_by_id.assert_called_once_with(999)
        assert result is None