# tests/downloadData/application/test_use_cases.py
import pytest
from unittest.mock import AsyncMock
from datetime import datetime,timezone

from app.downloadData.domain.models import DownloadedData
from app.users.domain.models import User

from app.downloadData.application.use_cases.add_downloaded_data import AddDownloadedDataUseCase
from app.downloadData.application.use_cases.get_downloaded_data_by_id import GetDownloadedDataByIdUseCase
from app.downloadData.application.use_cases.get_latest_downloaded_data_by_point import GetLatestDownloadedDataByPointUseCase
from app.downloadData.application.use_cases.list_all_downloadedData import ListAllDownloadedDataUseCase
from app.downloadData.application.use_cases.list_downloaded_data_by_point import ListDownloadedDataByPointUseCase


@pytest.mark.asyncio
async def test_add_downloaded_data_permission_denied():
    repo = AsyncMock()
    use_case = AddDownloadedDataUseCase(repo)
    data = DownloadedData(point_id=1, downloaded_at=datetime.now(timezone.utc), data={})
    user = User(id=1, username="user", email="u@example.com", hashed_password="xxx", is_admin=False, is_employee=True)

    with pytest.raises(PermissionError):
        await use_case.execute(data, user)

@pytest.mark.asyncio
async def test_add_downloaded_data_success():
    repo = AsyncMock()
    use_case = AddDownloadedDataUseCase(repo)
    data = DownloadedData(point_id=1, downloaded_at=datetime.now(timezone.utc), data={})
    user = User(id=2, username="admin", email="a@example.com", hashed_password="xxx", is_admin=True, is_employee=False)
    repo.add_downloaded_data.return_value = data

    result = await use_case.execute(data, user)
    repo.add_downloaded_data.assert_awaited_once_with(data)
    assert result == data

@pytest.mark.asyncio
async def test_get_downloaded_data_by_id_permission_denied():
    repo = AsyncMock()
    use_case = GetDownloadedDataByIdUseCase(repo)
    user = User(id=1, username="user", email="u@example.com", hashed_password="xxx", is_admin=False, is_employee=True)

    with pytest.raises(PermissionError):
        await use_case.execute(1, user)

@pytest.mark.asyncio
async def test_get_downloaded_data_by_id_success():
    repo = AsyncMock()
    use_case = GetDownloadedDataByIdUseCase(repo)
    user = User(id=2, username="admin", email="a@example.com", hashed_password="xxx", is_admin=True, is_employee=False)
    data = DownloadedData(point_id=1, downloaded_at=datetime.now(timezone.utc), data={}, id=1)
    repo.get_downloaded_data_by_id.return_value = data

    result = await use_case.execute(1, user)
    repo.get_downloaded_data_by_id.assert_awaited_once_with(1)
    assert result == data

@pytest.mark.asyncio
async def test_get_downloaded_data_by_id_not_found():
    repo = AsyncMock()
    use_case = GetDownloadedDataByIdUseCase(repo)
    user = User(id=2, username="admin", email="a@example.com", hashed_password="xxx", is_admin=True, is_employee=False)
    repo.get_downloaded_data_by_id.return_value = None

    with pytest.raises(ValueError):
        await use_case.execute(999, user)

@pytest.mark.asyncio
async def test_get_latest_downloaded_data_by_point_permission_denied():
    repo = AsyncMock()
    use_case = GetLatestDownloadedDataByPointUseCase(repo)
    user = User(id=1, username="user", email="u@example.com", hashed_password="xxx", is_admin=False, is_employee=True)

    with pytest.raises(PermissionError):
        await use_case.execute(1, user)

@pytest.mark.asyncio
async def test_get_latest_downloaded_data_by_point_success():
    repo = AsyncMock()
    use_case = GetLatestDownloadedDataByPointUseCase(repo)
    user = User(id=2, username="admin", email="a@example.com", hashed_password="xxx", is_admin=True, is_employee=False)
    data = DownloadedData(point_id=1, downloaded_at=datetime.now(timezone.utc), data={}, id=1)
    repo.get_latest_downloaded_data_by_point_id.return_value = data

    result = await use_case.execute(1, user)
    repo.get_latest_downloaded_data_by_point_id.assert_awaited_once_with(1)
    assert result == data

@pytest.mark.asyncio
async def test_get_latest_downloaded_data_by_point_not_found():
    repo = AsyncMock()
    use_case = GetLatestDownloadedDataByPointUseCase(repo)
    user = User(id=2, username="admin", email="a@example.com", hashed_password="xxx", is_admin=True, is_employee=False)
    repo.get_latest_downloaded_data_by_point_id.return_value = None

    with pytest.raises(ValueError):
        await use_case.execute(999, user)

@pytest.mark.asyncio
async def test_list_all_downloaded_data_permission_denied():
    repo = AsyncMock()
    use_case = ListAllDownloadedDataUseCase(repo)
    user = User(id=1, username="user", email="u@example.com", hashed_password="xxx", is_admin=False, is_employee=True)

    with pytest.raises(PermissionError):
        await use_case.execute(user)

@pytest.mark.asyncio
async def test_list_all_downloaded_data_success():
    repo = AsyncMock()
    use_case = ListAllDownloadedDataUseCase(repo)
    user = User(id=2, username="admin", email="a@example.com", hashed_password="xxx", is_admin=True, is_employee=False)
    data_list = [
        DownloadedData(point_id=1, downloaded_at=datetime.now(timezone.utc), data={}, id=1),
        DownloadedData(point_id=2, downloaded_at=datetime.now(timezone.utc), data={}, id=2),
    ]
    repo.list_all_downloaded_data.return_value = data_list

    result = await use_case.execute(user)
    repo.list_all_downloaded_data.assert_awaited_once()
    assert result == data_list

@pytest.mark.asyncio
async def test_list_downloaded_data_by_point_permission_denied():
    repo = AsyncMock()
    use_case = ListDownloadedDataByPointUseCase(repo)
    user = User(id=1, username="user", email="u@example.com", hashed_password="xxx", is_admin=False, is_employee=True)

    with pytest.raises(PermissionError):
        await use_case.execute(1, user)

@pytest.mark.asyncio
async def test_list_downloaded_data_by_point_success():
    repo = AsyncMock()
    use_case = ListDownloadedDataByPointUseCase(repo)
    user = User(id=2, username="admin", email="a@example.com", hashed_password="xxx", is_admin=True, is_employee=False)
    data_list = [
        DownloadedData(point_id=1, downloaded_at=datetime.now(timezone.utc), data={}, id=1),
        DownloadedData(point_id=1, downloaded_at=datetime.now(timezone.utc), data={}, id=2),
    ]
    repo.list_downloaded_data_by_point_id.return_value = data_list

    result = await use_case.execute(1, user)
    repo.list_downloaded_data_by_point_id.assert_awaited_once_with(1)
    assert result == data_list