import pytest
import asyncio
from unittest.mock import AsyncMock
from app.hindcastPoint.application.use_cases.ListHindcastPointUseCase import ListHindCastPointUseCase
from app.hindcastPoint.domain.models import HindcastPoint
from app.users.domain.models import User

@pytest.mark.asyncio
class TestListHindCastPointUseCase:

    @pytest.fixture
    def admin_user(self):
        return User(id=1, username="admin", email="admin@example.com", hashed_password="hashed", is_admin=True, is_employee=False)

    @pytest.fixture
    def normal_user(self):
        return User(id=2, username="user", email="user@example.com", hashed_password="hashed", is_admin=False, is_employee=False)

    @pytest.fixture
    def repo_mock(self):
        mock = AsyncMock()
        mock.list_hindcastPoint = AsyncMock(return_value=[
            HindcastPoint(latitude=1.0, longitude=2.0, url="url1", models=["model1"]),
            HindcastPoint(latitude=3.0, longitude=4.0, url="url2", models=["model2", "model3"]),
        ])
        return mock

    @pytest.fixture
    def use_case(self, repo_mock):
        return ListHindCastPointUseCase(repo_mock)

    async def test_execute_returns_list_of_hindcast_points(self, use_case, admin_user):
        result = await use_case.execute(admin_user)
        assert isinstance(result, list)
        assert all(isinstance(item, HindcastPoint) for item in result)
        assert len(result) == 2

    async def test_execute_raises_permission_error_for_non_admin(self, use_case, normal_user):
        with pytest.raises(PermissionError):
            await use_case.execute(normal_user)

    async def test_execute_calls_repo_list_hindcastPoint_once(self, use_case, admin_user, repo_mock):
        await use_case.execute(admin_user)
        repo_mock.list_hindcastPoint.assert_awaited_once()

    async def test_execute_raises_permission_error_if_requester_none(self, use_case):
        with pytest.raises(PermissionError):
            await use_case.execute(None)

    async def test_execute_empty_list(self, use_case, admin_user, repo_mock):
        repo_mock.list_hindcastPoint.return_value = []
        result = await use_case.execute(admin_user)
        assert result == []

    async def test_execute_repo_raises_exception_bubbles_up(self, use_case, admin_user, repo_mock):
        repo_mock.list_hindcastPoint.side_effect = Exception("DB error")
        with pytest.raises(Exception) as exc:
            await use_case.execute(admin_user)
        assert str(exc.value) == "DB error"

    async def test_execute_with_user_without_is_admin_attr_raises_permission(self, use_case):
        class DummyUser:
            pass
        dummy = DummyUser()
        with pytest.raises(PermissionError):
            await use_case.execute(dummy)

    async def test_execute_with_user_is_admin_false_raises_permission(self, use_case):
        class DummyUser:
            is_admin = False
        dummy = DummyUser()
        with pytest.raises(PermissionError):
            await use_case.execute(dummy)
