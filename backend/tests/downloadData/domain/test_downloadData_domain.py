import pytest
from datetime import datetime, timezone
from app.downloadData.domain.models import DownloadedData

def test_downloaded_data_creation():
    dd = DownloadedData(point_id=1, downloaded_at=datetime.now(timezone.utc), data={"key": "value"})
    assert dd.point_id == 1
    assert isinstance(dd.downloaded_at, datetime)
    assert dd.data == {"key": "value"}
    assert dd.id is None

def test_downloaded_data_with_id():
    dd = DownloadedData(point_id=2, downloaded_at=datetime.now(timezone.utc), data={"a": 123}, id=10)
    assert dd.id == 10

def test_downloaded_at_is_datetime():
    dt = datetime.now(timezone.utc)
    dd = DownloadedData(point_id=3, downloaded_at=dt, data={})
    assert dd.downloaded_at == dt

def test_data_accepts_any_json():
    json_data = {"nested": {"list": [1, 2, 3]}, "bool": True}
    dd = DownloadedData(point_id=4, downloaded_at=datetime.now(timezone.utc), data=json_data)
    assert dd.data["nested"]["list"] == [1, 2, 3]
    assert dd.data["bool"] is True



def test_id_optional_field():
    dd1 = DownloadedData(point_id=5, downloaded_at=datetime.now(timezone.utc), data={})
    dd2 = DownloadedData(point_id=5, downloaded_at=datetime.now(timezone.utc), data={}, id=None)
    assert dd1.id is None
    assert dd2.id is None

def test_equality_of_instances():
    dt = datetime.now(timezone.utc)
    dd1 = DownloadedData(point_id=6, downloaded_at=dt, data={"x": 1}, id=100)
    dd2 = DownloadedData(point_id=6, downloaded_at=dt, data={"x": 1}, id=100)
    assert dd1 == dd2

def test_inequality_different_point_id():
    dt = datetime.now(timezone.utc)
    dd1 = DownloadedData(point_id=7, downloaded_at=dt, data={"x": 1})
    dd2 = DownloadedData(point_id=8, downloaded_at=dt, data={"x": 1})
    assert dd1 != dd2