import pytest
from unittest.mock import AsyncMock
from datetime import datetime, timezone
from typing import Any

from app.forecast_system_results.domain.models import ForecastSystemResult
from app.forecast_zones.domain.models import ForecastZone
from app.users.domain.models import User

from app.forecast_system_results.application.use_cases.CreateForecastSystemResultUseCase import CreateForecastSystemResultUseCase

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

class TestCreateForecastSystemResultUseCase:

    @pytest.mark.asyncio
    async def test_create_result_as_admin_success(self, mock_result_repo, mock_zone_repo, admin_user, sample_forecast_zone):
        mock_zone_repo.get_forecast_zone_by_id.return_value = sample_forecast_zone
        
        expected_result = ForecastSystemResult(
            id=1,
            forecast_zone_id=sample_forecast_zone.id,
            execution_date=datetime.now(timezone.utc),
            result_data={"Hs": 2.0}
        )
        mock_result_repo.create_forecast_system_result.return_value = expected_result

        use_case = CreateForecastSystemResultUseCase(mock_result_repo, mock_zone_repo)
        
        result_data = {"Hs": 2.0, "Tp": 5.0}
        created_result = await use_case.execute(sample_forecast_zone.id, result_data, admin_user)

        mock_zone_repo.get_forecast_zone_by_id.assert_called_once_with(sample_forecast_zone.id)
        mock_result_repo.create_forecast_system_result.assert_called_once()
        
        args, _ = mock_result_repo.create_forecast_system_result.call_args
        passed_result = args[0]
        assert passed_result.forecast_zone_id == sample_forecast_zone.id
        assert passed_result.result_data == result_data
        assert isinstance(passed_result.execution_date, datetime)
        assert passed_result.id is None

        assert created_result == expected_result

    @pytest.mark.asyncio
    async def test_create_result_as_employee_success(self, mock_result_repo, mock_zone_repo, employee_user, sample_forecast_zone):
        mock_zone_repo.get_forecast_zone_by_id.return_value = sample_forecast_zone
        expected_result = ForecastSystemResult(
            id=1,
            forecast_zone_id=sample_forecast_zone.id,
            execution_date=datetime.now(timezone.utc),
            result_data={"Hs": 2.0}
        )
        mock_result_repo.create_forecast_system_result.return_value = expected_result

        use_case = CreateForecastSystemResultUseCase(mock_result_repo, mock_zone_repo)
        created_result = await use_case.execute(sample_forecast_zone.id, {"Hs": 2.0}, employee_user)

        mock_zone_repo.get_forecast_zone_by_id.assert_called_once_with(sample_forecast_zone.id)
        mock_result_repo.create_forecast_system_result.assert_called_once()
        assert created_result == expected_result

    @pytest.mark.asyncio
    async def test_create_result_permission_denied_for_client(self, mock_result_repo, mock_zone_repo, client_user, sample_forecast_zone):
        use_case = CreateForecastSystemResultUseCase(mock_result_repo, mock_zone_repo)

        with pytest.raises(PermissionError, match="Solo los administradores o empleados pueden crear resultados de previsión."):
            await use_case.execute(sample_forecast_zone.id, {"Hs": 2.0}, client_user)

        mock_zone_repo.get_forecast_zone_by_id.assert_not_called()
        mock_result_repo.create_forecast_system_result.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_result_forecast_zone_not_found(self, mock_result_repo, mock_zone_repo, admin_user):
        mock_zone_repo.get_forecast_zone_by_id.return_value = None

        use_case = CreateForecastSystemResultUseCase(mock_result_repo, mock_zone_repo)

        with pytest.raises(ValueError, match="La ForecastZone con ID 999 no existe."):
            await use_case.execute(999, {"Hs": 2.0}, admin_user)

        mock_zone_repo.get_forecast_zone_by_id.assert_called_once_with(999)
        mock_result_repo.create_forecast_system_result.assert_not_called()