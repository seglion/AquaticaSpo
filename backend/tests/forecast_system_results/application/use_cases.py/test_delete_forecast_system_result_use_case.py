import pytest
from unittest.mock import AsyncMock

from app.users.domain.models import User

from app.forecast_system_results.application.use_cases.DeleteForecastSystemResultUseCase import DeleteForecastSystemResultUseCase

@pytest.fixture
def mock_result_repo():
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

class TestDeleteForecastSystemResultUseCase:

    @pytest.mark.asyncio
    async def test_delete_result_as_admin_success(self, mock_result_repo, admin_user):
        mock_result_repo.delete_forecast_system_result.return_value = True
        
        use_case = DeleteForecastSystemResultUseCase(mock_result_repo)
        deleted = await use_case.execute(1, admin_user)

        mock_result_repo.delete_forecast_system_result.assert_called_once_with(1)
        assert deleted is True

    @pytest.mark.asyncio
    async def test_delete_result_permission_denied_for_employee(self, mock_result_repo, employee_user):
        use_case = DeleteForecastSystemResultUseCase(mock_result_repo)

        with pytest.raises(PermissionError, match="Solo los administradores pueden eliminar resultados de previsión."):
            await use_case.execute(1, employee_user)

        mock_result_repo.delete_forecast_system_result.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_result_permission_denied_for_client(self, mock_result_repo, client_user):
        use_case = DeleteForecastSystemResultUseCase(mock_result_repo)

        with pytest.raises(PermissionError, match="Solo los administradores pueden eliminar resultados de previsión."):
            await use_case.execute(1, client_user)

        mock_result_repo.delete_forecast_system_result.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_result_not_found(self, mock_result_repo, admin_user):
        mock_result_repo.delete_forecast_system_result.return_value = False
        
        use_case = DeleteForecastSystemResultUseCase(mock_result_repo)

        with pytest.raises(ValueError, match="Resultado de previsión con ID 999 no encontrado para eliminar."):
            await use_case.execute(999, admin_user)

        mock_result_repo.delete_forecast_system_result.assert_called_once_with(999)