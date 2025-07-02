import pytest
from unittest.mock import AsyncMock
from app.hindcastPoint.domain.models import HindcastPoint
from app.users.domain.models import User
from app.hindcastPoint.application.use_cases.UpdateHindcastPointUseCase import UpdateHindCastPointUseCase

class TestUpdateHindCastPointUseCase:

    @pytest.fixture
    def repo_mock(self):
        repo = AsyncMock()
        repo.update_hindcastPoint = AsyncMock()
        return repo

    @pytest.fixture
    def admin_user(self):
        return User(id=1, username="admin", email="admin@example.com", hashed_password="hashed", is_admin=True, is_employee=False)

    @pytest.fixture
    def normal_user(self):
        return User(id=2, username="user", email="user@example.com", hashed_password="hashed", is_admin=False, is_employee=False)

    @pytest.fixture
    def hindcast_point(self):
        return HindcastPoint( latitude=10.0, longitude=20.0, url="url", models=None)

    @pytest.mark.asyncio
    async def test_update_success_with_admin(self, repo_mock, admin_user, hindcast_point):
        repo_mock.update_hindcastPoint.return_value = hindcast_point
        use_case = UpdateHindCastPointUseCase(repo_mock)
        
        result = await use_case.execute(hindcast_point, admin_user)
        
        repo_mock.update_hindcastPoint.assert_awaited_once_with(hindcast_point)
        assert result == hindcast_point

    @pytest.mark.asyncio
    async def test_update_raises_permission_error_if_not_admin(self, repo_mock, normal_user, hindcast_point):
        use_case = UpdateHindCastPointUseCase(repo_mock)
        
        with pytest.raises(PermissionError):
            await use_case.execute(hindcast_point, normal_user)
        
        repo_mock.update_hindcastPoint.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_raises_type_error_if_hindcast_point_invalid(self, repo_mock, admin_user):
        use_case = UpdateHindCastPointUseCase(repo_mock)
        
        with pytest.raises(TypeError):
            await use_case.execute("not a HindcastPoint", admin_user)

    @pytest.mark.asyncio
    async def test_update_raises_type_error_if_requester_invalid(self, repo_mock, hindcast_point):
        use_case = UpdateHindCastPointUseCase(repo_mock)
        
        with pytest.raises(AttributeError):
            await use_case.execute(hindcast_point, None)  # requester is None, no is_admin attribute

    @pytest.mark.asyncio
    async def test_update_calls_repo_once(self, repo_mock, admin_user, hindcast_point):
        use_case = UpdateHindCastPointUseCase(repo_mock)
        await use_case.execute(hindcast_point, admin_user)
        
        repo_mock.update_hindcastPoint.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_returns_updated_hindcast_point(self, repo_mock, admin_user, hindcast_point):
        repo_mock.update_hindcastPoint.return_value = hindcast_point
        use_case = UpdateHindCastPointUseCase(repo_mock)

        result = await use_case.execute(hindcast_point, admin_user)
        assert isinstance(result, HindcastPoint)

    @pytest.mark.asyncio
    async def test_update_raises_exception_if_repo_raises(self, repo_mock, admin_user, hindcast_point):
        repo_mock.update_hindcastPoint.side_effect = Exception("DB error")
        use_case = UpdateHindCastPointUseCase(repo_mock)

        with pytest.raises(Exception) as exc:
            await use_case.execute(hindcast_point, admin_user)
        assert "DB error" in str(exc.value)

    @pytest.mark.asyncio
    async def test_update_permission_check_first(self, repo_mock, normal_user, hindcast_point):
        use_case = UpdateHindCastPointUseCase(repo_mock)

        with pytest.raises(PermissionError):
            await use_case.execute(hindcast_point, normal_user)
        repo_mock.update_hindcastPoint.assert_not_called()