import pytest
from unittest.mock import AsyncMock
from app.hindcastPoint.application.use_cases.DeleteHindcastPointUseCase import DeleteHindCastUseCase
from app.users.domain.models import User

@pytest.fixture
def admin_user():
    return User(
        id=1,
        username="admin",
        email="admin@example.com",
        hashed_password="hashed_pw_dummy",
        is_admin=True,
        is_employee=False,
    )

@pytest.fixture
def normal_user():
    return User(
        id=2,
        username="user",
        email="user@example.com",
        hashed_password="hashed_pw_dummy",
        is_admin=False,
        is_employee=False,
    )
@pytest.mark.asyncio
class TestDeleteHindCastUseCase:

    @pytest.fixture
    def repo_mock(self):
        return AsyncMock()


    @pytest.fixture
    def use_case(self, repo_mock):
        return DeleteHindCastUseCase(repo_mock)

    async def test_admin_can_delete_successfully(self, use_case, repo_mock, admin_user):
        repo_mock.delete_hindcastPoint.return_value = True
        result = await use_case.execute(1, admin_user)
        assert result is None
        repo_mock.delete_hindcastPoint.assert_awaited_once_with(1)

    async def test_delete_nonexistent_point_raises_value_error(self, use_case, repo_mock, admin_user):
        repo_mock.delete_hindcastPoint.return_value = False
        with pytest.raises(ValueError) as exc:
            await use_case.execute(999, admin_user)
        assert str(exc.value) == "Punto Hindcast no encontrado"
        repo_mock.delete_hindcastPoint.assert_awaited_once_with(999)

    async def test_non_admin_raises_permission_error(self, use_case, repo_mock, normal_user):
        with pytest.raises(PermissionError) as exc:
            await use_case.execute(1, normal_user)
        assert str(exc.value) == "Solo admin puede borrar puntos Hindcast"
        repo_mock.delete_hindcastPoint.assert_not_awaited()

    async def test_delete_called_with_correct_id(self, use_case, repo_mock, admin_user):
        repo_mock.delete_hindcastPoint.return_value = True
        await use_case.execute(42, admin_user)
        repo_mock.delete_hindcastPoint.assert_awaited_once_with(42)

    async def test_delete_raises_type_error_with_invalid_id(self, use_case, repo_mock, admin_user):
        with pytest.raises(TypeError):
            await use_case.execute("not-an-int", admin_user)
        repo_mock.delete_hindcastPoint.assert_not_awaited()

    async def test_delete_raises_permission_error_with_none_requester(self, use_case, repo_mock):
        with pytest.raises(AttributeError):
            await use_case.execute(1, None)
        repo_mock.delete_hindcastPoint.assert_not_awaited()

    async def test_delete_raises_permission_error_when_requester_missing_admin_flag(self, use_case, repo_mock):
        class FakeUser:
            pass
        with pytest.raises(AttributeError):
            await use_case.execute(1, FakeUser())
        repo_mock.delete_hindcastPoint.assert_not_awaited()

    async def test_delete_does_not_call_repo_if_permission_denied(self, use_case, repo_mock, normal_user):
        with pytest.raises(PermissionError):
            await use_case.execute(1, normal_user)
        repo_mock.delete_hindcastPoint.assert_not_awaited()