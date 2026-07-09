import pytest
import asyncio
from unittest.mock import AsyncMock
from app.hindcastPoint.application.use_cases.CreateHindcastPointUseCase import CreateHindcasPointtUseCase # Corrige el import si es CreateHindcastPointUseCase
from app.hindcastPoint.domain.models import HindcastPoint
from app.users.domain.models import User

@pytest.mark.asyncio
async def test_create_hindcast_point_success():
    repo_mock = AsyncMock()
    # Mock que devuelva el mismo HindcastPoint
    repo_mock.create_hindcastPoint = AsyncMock(return_value=HindcastPoint(latitude=1.0, longitude=2.0, url="url"))

    use_case = CreateHindcasPointtUseCase(repo_mock)  # Cambia si renombraste la clase

    requester = User(id=1, username="admin", is_admin=True, email="a@a.com", hashed_password="x", is_employee=False)
    hindcast_point = HindcastPoint(latitude=1.0, longitude=2.0, url="url")

    result = await use_case.execute(hindcast_point, requester)
    repo_mock.create_hindcastPoint.assert_awaited_once_with(hindcast_point)
    assert result.latitude == hindcast_point.latitude
    assert result.longitude == hindcast_point.longitude
    assert result.url == hindcast_point.url

@pytest.mark.asyncio
async def test_create_hindcast_point_permission_error():
    repo_mock = AsyncMock()
    use_case = CreateHindcasPointtUseCase(repo_mock)

    requester = User(id=2, username="user", is_admin=False, email="u@u.com", hashed_password="y", is_employee=False)
    hindcast_point = HindcastPoint(latitude=1.0, longitude=2.0, url="url")

    with pytest.raises(PermissionError):
        await use_case.execute(hindcast_point, requester)
    repo_mock.create_hindcastPoint.assert_not_awaited()