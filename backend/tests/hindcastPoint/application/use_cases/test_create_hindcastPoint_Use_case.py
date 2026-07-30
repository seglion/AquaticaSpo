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
async def test_create_hindcast_point_with_wind_fields():
    repo_mock = AsyncMock()
    expected = HindcastPoint(
        latitude=1.0, longitude=2.0, url="https://marine-api.open-meteo.com/v1/marine",
        models=["wavewatch3"],
        wind_url="https://api.open-meteo.com/v1/forecast",
        wind_models=["best_match"],
    )
    repo_mock.create_hindcastPoint = AsyncMock(return_value=expected)

    use_case = CreateHindcasPointtUseCase(repo_mock)
    requester = User(id=1, username="admin", is_admin=True, email="a@a.com", hashed_password="x", is_employee=False)

    result = await use_case.execute(expected, requester)
    repo_mock.create_hindcastPoint.assert_awaited_once_with(expected)
    assert result.wind_url == "https://api.open-meteo.com/v1/forecast"
    assert result.wind_models == ["best_match"]

@pytest.mark.asyncio
async def test_create_hindcast_point_permission_error():
    repo_mock = AsyncMock()
    use_case = CreateHindcasPointtUseCase(repo_mock)

    requester = User(id=2, username="user", is_admin=False, email="u@u.com", hashed_password="y", is_employee=False)
    hindcast_point = HindcastPoint(latitude=1.0, longitude=2.0, url="url")

    with pytest.raises(PermissionError):
        await use_case.execute(hindcast_point, requester)
    repo_mock.create_hindcastPoint.assert_not_awaited()