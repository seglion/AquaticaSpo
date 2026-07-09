import pytest
from app.ports.domain.models import Port

def test_port_has_name():
    port = Port(name="Test Port",country="Test Country",longitude=0.0,latitude=0.0)
    assert hasattr(port, "name")

def test_port_name_is_string():
    port = Port(name="Test Port",country="Test Country",longitude=0.0,latitude=0.0)

    assert isinstance(port.name, str)

def test_port_has_country():
    port = Port(name="Test Port",country="Test Country",longitude=0.0,latitude=0.0)
    assert hasattr(port, "country")

def test_port_country_is_string():
    port = Port(name="Test Port",country="Test Country",longitude=0.0,latitude=0.0)
    assert isinstance(port.country, str)
    
def test_port_has_longitude():
    port = Port(name="Test Port",country="Test Country",longitude=0.0,latitude=0.0)
    assert hasattr(port, "longitude")

def test_port_longitude_is_float():
    port = Port(name="Test Port",country="Test Country",longitude=0.0,latitude=0.0)
    assert isinstance(port.longitude, float)
    
def test_port_has_latitude():
    port = Port(name="Test Port",country="Test Country",longitude=0.0,latitude=0.0)
    assert hasattr(port, "latitude")

def test_port_latitude_is_float():
    port = Port(name="Test Port",country="Test Country",longitude=0.0,latitude=0.0)
    assert isinstance(port.latitude, float)