import pytest
import asyncio
from unittest.mock import AsyncMock
from app.hindcastPoint.application.use_cases.GetHindcastPointUseCase import GetContractUseCase
from app.hindcastPoint.domain.models import HindcastPoint
from app.users.domain.models import User

@pytest.fixture
def admin_user():
    return User(id=1, username="admin", email="admin@example.com", hashed_password="hash", is_admin=True, is_employee=False)

@pytest.fixture
def normal_user():
    return User(id=2, username="user", email="user@example.com", hashed_password="hash", is_admin=False, is_employee=False)

@pytest.fixture
def repo_mock():
    repo = AsyncMock()
    return repo

@pytest.mark.asyncio
class TestGetHindcastPointUseCase:

    async def test_admin_can_get_hindcast_point_successfully(self, repo_mock, admin_user):
        use_case = GetContractUseCase(repo_mock)
        expected_point = HindcastPoint(latitude=1.0, longitude=2.0, url="url")
        repo_mock.get_hindcastPoint_by_id.return_value = expected_point
        
        result = await use_case.execute(1, admin_user)

        repo_mock.get_hindcastPoint_by_id.assert_awaited_once_with(1)
        assert result == expected_point

    async def test_non_admin_raises_permission_error(self, repo_mock, normal_user):
        use_case = GetContractUseCase(repo_mock)
        
        with pytest.raises(PermissionError):
            await use_case.execute(1, normal_user)

        repo_mock.get_hindcastPoint_by_id.assert_not_awaited()

    async def test_return_none_if_hindcast_point_not_found(self, repo_mock, admin_user):
        use_case = GetContractUseCase(repo_mock)
        repo_mock.get_hindcastPoint_by_id.return_value = None
        
        result = await use_case.execute(999, admin_user)

        assert result is None

    async def test_repo_called_with_correct_id(self, repo_mock, admin_user):
        use_case = GetContractUseCase(repo_mock)
        repo_mock.get_hindcastPoint_by_id.return_value = HindcastPoint(latitude=0, longitude=0, url="url")
        
        await use_case.execute(42, admin_user)

        repo_mock.get_hindcastPoint_by_id.assert_awaited_once_with(42)

    async def test_execute_raises_type_error_if_id_not_int(self, repo_mock, admin_user):
        use_case = GetContractUseCase(repo_mock)
        
        with pytest.raises(TypeError):
            await use_case.execute("invalid_id", admin_user)

        repo_mock.get_hindcastPoint_by_id.assert_not_awaited()

    async def test_execute_raises_permission_error_if_user_is_none(self, repo_mock):
        use_case = GetContractUseCase(repo_mock)
        
        with pytest.raises(PermissionError):
            await use_case.execute(1, None)

        repo_mock.get_hindcastPoint_by_id.assert_not_awaited()

    async def test_execute_returns_hindcast_point_with_models_list(self, repo_mock, admin_user):
        use_case = GetContractUseCase(repo_mock)
        point_with_models = HindcastPoint(latitude=1, longitude=1, url="url", models=["model1", "model2"])
        repo_mock.get_hindcastPoint_by_id.return_value = point_with_models
        
        result = await use_case.execute(1, admin_user)

        assert result.models == ["model1", "model2"]

    async def test_repo_raises_exception_is_propagated(self, repo_mock, admin_user):
        use_case = GetContractUseCase(repo_mock)
        repo_mock.get_hindcastPoint_by_id.side_effect = Exception("DB error")
        
        with pytest.raises(Exception, match="DB error"):
            await use_case.execute(1, admin_user)
