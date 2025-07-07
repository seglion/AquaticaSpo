import pytest
from unittest.mock import AsyncMock
from datetime import datetime, timezone

from app.forecast_system_results.domain.models import ForecastSystemResult
from app.forecast_zones.domain.models import ForecastZone
from app.users.domain.models import User

from app.forecast_system_results.application.use_cases.GetLatestForecastSystemResultByZoneUseCase import GetLatestForecastSystemResultByZoneUseCase

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
def sample_forecast_zone():
    """Zona de previsión de ejemplo adaptada a tu modelo ForecastZone real."""
    return ForecastZone(
        id=101,
        name="Test Zone Point",
        description="A test point forecast zone.",
        forecast_system_id=1,
        geom={"type": "Point", "coordinates": [0.0, 0.0]}
    )

@pytest.fixture
def latest_sample_result(sample_forecast_zone):
    return ForecastSystemResult(
        id=3,
        forecast_zone_id=sample_forecast_zone.id,
        execution_date=datetime.now(timezone.utc),
        result_data={"Hs": 3.0, "latest": True}
    )

class TestGetLatestForecastSystemResultByZoneUseCase:

    @pytest.mark.asyncio
    async def test_get_latest_result_as_admin_success(self, mock_result_repo, mock_zone_repo, admin_user, sample_forecast_zone, latest_sample_result):
        mock_zone_repo.get_forecast_zone_by_id.return_value = sample_forecast_zone
        mock_result_repo.get_latest_result_by_zone.return_value = latest_sample_result
        
        use_case = GetLatestForecastSystemResultByZoneUseCase(mock_result_repo, mock_zone_repo)
        result = await use_case.execute(sample_forecast_zone.id, admin_user)

        mock_zone_repo.get_forecast_zone_by_id.assert_called_once_with(sample_forecast_zone.id)
        mock_result_repo.get_latest_result_by_zone.assert_called_once_with(sample_forecast_zone.id)
        assert result == latest_sample_result

    @pytest.mark.asyncio
    async def test_get_latest_result_as_employee_success(self, mock_result_repo, mock_zone_repo, employee_user, sample_forecast_zone, latest_sample_result):
        mock_zone_repo.get_forecast_zone_by_id.return_value = sample_forecast_zone
        mock_result_repo.get_latest_result_by_zone.return_value = latest_sample_result
        
        use_case = GetLatestForecastSystemResultByZoneUseCase(mock_result_repo, mock_zone_repo)
        result = await use_case.execute(sample_forecast_zone.id, employee_user)

        mock_zone_repo.get_forecast_zone_by_id.assert_called_once_with(sample_forecast_zone.id)
        mock_result_repo.get_latest_result_by_zone.assert_called_once_with(sample_forecast_zone.id)
        assert result == latest_sample_result

    @pytest.mark.asyncio
    async def test_get_latest_result_permission_denied_for_client(self, mock_result_repo, mock_zone_repo, client_user, sample_forecast_zone):
        mock_zone_repo.get_forecast_zone_by_id.return_value = sample_forecast_zone

        use_case = GetLatestForecastSystemResultByZoneUseCase(mock_result_repo, mock_zone_repo)

        with pytest.raises(PermissionError, match="No tienes permiso para ver el último resultado de previsión."):
            await use_case.execute(sample_forecast_zone.id, client_user)

        mock_zone_repo.get_forecast_zone_by_id.assert_not_called()
        mock_result_repo.get_latest_result_by_zone.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_latest_result_forecast_zone_not_found(self, mock_result_repo, mock_zone_repo, admin_user):
        mock_zone_repo.get_forecast_zone_by_id.return_value = None

        use_case = GetLatestForecastSystemResultByZoneUseCase(mock_result_repo, mock_zone_repo)

        with pytest.raises(ValueError, match="La ForecastZone con ID 999 no existe."):
            await use_case.execute(999, admin_user)

        mock_zone_repo.get_forecast_zone_by_id.assert_called_once_with(999)
        mock_result_repo.get_latest_result_by_zone.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_latest_result_returns_none_if_no_results(self, mock_result_repo, mock_zone_repo, admin_user, sample_forecast_zone):
        mock_zone_repo.get_forecast_zone_by_id.return_value = sample_forecast_zone
        mock_result_repo.get_latest_result_by_zone.return_value = None
        
        use_case = GetLatestForecastSystemResultByZoneUseCase(mock_result_repo, mock_zone_repo)
        result = await use_case.execute(sample_forecast_zone.id, admin_user)

        mock_result_repo.get_latest_result_by_zone.assert_called_once_with(sample_forecast_zone.id)
        assert result is None