import json
import pytest
from unittest.mock import AsyncMock
from app.forecastSystem.infrastructure.repositories import ForecastWorkerRepository
from app.forecastSystem.domain.models import ForecastZone
from app.users.domain.models import User


@pytest.fixture
def repo():
    r = ForecastWorkerRepository()
    r._request_authed = AsyncMock()
    return r


@pytest.fixture
def requester():
    return User(
        id=1, is_admin=True, session_USER="test-token",
    )


@pytest.fixture
def zones():
    return [
        ForecastZone(id=1, name="Zona1", description="D1", geom={"type": "Point", "coordinates": [0, 0]}, forecast_system_id=1),
        ForecastZone(id=2, name="Zona2", description="D2", geom={"type": "Point", "coordinates": [1, 1]}, forecast_system_id=1),
    ]


@pytest.fixture
def propagation_json():
    return json.dumps({
        "ewam": {
            "timestamps": ["2026-07-30T10:00:00Z", "2026-07-30T11:00:00Z"],
            "zones": {
                "Zona1": {"Hs": [1.5, 1.8], "Tp": [6.0, 6.5], "PeakDirection": [270, 275], "Tide": [1.0, 1.1], "CotaRu2p": [3.0, 3.2], "CotaRu1p": [2.5, 2.7], "Ru2p": [1.8, 2.0], "Ru1p": [1.5, 1.7]},
                "Zona2": {"Hs": [1.2, 1.4], "Tp": [5.5, 6.0], "PeakDirection": [265, 270], "Tide": [0.9, 1.0], "CotaRu2p": [2.8, 3.0], "CotaRu1p": [2.3, 2.5], "Ru2p": [1.6, 1.8], "Ru1p": [1.3, 1.5]},
            },
        },
    })


async def test_save_without_wind(repo, requester, zones, propagation_json):
    repo._request_authed.return_value.status_code = 201

    result = await repo.save_forecast_results(1, zones, propagation_json, requester)

    assert repo._request_authed.awaited
    for call in repo._request_authed.call_args_list:
        args, kwargs = call
        assert args[0] == "POST"
        assert args[1] == "/forecast-results/"
        payload = kwargs.get("json", {})
        hourly = payload.get("result_data", {}).get("hourly", {})
        assert "wind_speed_10m" not in hourly
        assert "wave_height_ewam" in hourly
    assert len(repo._request_authed.call_args_list) == 2


async def test_save_with_wind_data(repo, requester, zones, propagation_json):
    repo._request_authed.return_value.status_code = 201
    wind_data = {
        "wind_speed_10m": [5.2, 6.1],
        "wind_gusts_10m": [8.0, 9.5],
        "wind_direction_10m": [180, 190],
    }

    await repo.save_forecast_results(1, zones, propagation_json, requester, wind_data=wind_data)

    for call in repo._request_authed.call_args_list:
        args, kwargs = call
        payload = kwargs.get("json", {})
        hourly = payload.get("result_data", {}).get("hourly", {})
        assert hourly["wind_speed_10m"] == [5.2, 6.1]
        assert hourly["wind_gusts_10m"] == [8.0, 9.5]
        assert hourly["wind_direction_10m"] == [180, 190]
        assert "wave_height_ewam" in hourly


async def test_save_with_partial_wind_data(repo, requester, zones, propagation_json):
    repo._request_authed.return_value.status_code = 201
    wind_data = {"wind_speed_10m": [3.0, 4.0]}

    await repo.save_forecast_results(1, zones, propagation_json, requester, wind_data=wind_data)

    for call in repo._request_authed.call_args_list:
        args, kwargs = call
        hourly = kwargs.get("json", {}).get("result_data", {}).get("hourly", {})
        assert hourly["wind_speed_10m"] == [3.0, 4.0]
        assert "wind_gusts_10m" not in hourly
        assert "wind_direction_10m" not in hourly


async def test_save_wind_added_to_all_zones(repo, requester, zones, propagation_json):
    repo._request_authed.return_value.status_code = 201
    wind_data = {
        "wind_speed_10m": [5.0, 6.0],
        "wind_direction_10m": [200, 210],
    }

    await repo.save_forecast_results(1, zones, propagation_json, requester, wind_data=wind_data)

    for call in repo._request_authed.call_args_list:
        args, kwargs = call
        payload = kwargs.get("json", {})
        hourly = payload.get("result_data", {}).get("hourly", {})
        assert hourly["wind_speed_10m"] == [5.0, 6.0]

    payloads_by_zone = {}
    for call in repo._request_authed.call_args_list:
        args, kwargs = call
        payload = kwargs.get("json", {})
        zid = payload.get("forecast_zone_id")
        payloads_by_zone[zid] = payload

    assert payloads_by_zone[1]["result_data"]["hourly"]["wind_speed_10m"] == [5.0, 6.0]
    assert payloads_by_zone[2]["result_data"]["hourly"]["wind_speed_10m"] == [5.0, 6.0]
