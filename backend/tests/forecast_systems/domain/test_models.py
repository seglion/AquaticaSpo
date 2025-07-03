# tests/forecast_systems/domain/test_models.py
import pytest
from app.forecastSystems.domain.models import ForecastSystem

def test_forecast_system_creation_with_only_required_fields():
    """
    Verifica que un ForecastSystem se puede crear con solo los campos obligatorios.
    """
    system = ForecastSystem(name="Sistema de Prueba A")
    
    assert system.id is None
    assert system.name == "Sistema de Prueba A"
    assert system.contract_id is None
    assert system.port_id is None
    assert system.hindcast_point_id is None

def test_forecast_system_creation_with_all_fields():
    """
    Verifica que un ForecastSystem se puede crear con todos los campos.
    """
    system = ForecastSystem(
        id=1,
        name="Sistema de Prueba B",
        contract_id=101,
        port_id=202,
        hindcast_point_id=303
    )
    
    assert system.id == 1
    assert system.name == "Sistema de Prueba B"
    assert system.contract_id == 101
    assert system.port_id == 202
    assert system.hindcast_point_id == 303

def test_forecast_system_equality():
    """
    Verifica que dos objetos ForecastSystem con los mismos atributos son considerados iguales.
    """
    system1 = ForecastSystem(id=1, name="Sistema X", contract_id=1)
    system2 = ForecastSystem(id=1, name="Sistema X", contract_id=1)
    system3 = ForecastSystem(id=2, name="Sistema Y", contract_id=2)

    assert system1 == system2
    assert system1 != system3

def test_forecast_system_representation():
    """
    Verifica la representación de cadena (repr) de un ForecastSystem.
    """
    system = ForecastSystem(id=1, name="Sistema Z", contract_id=5)
    # Por defecto, el __repr__ de un dataclass es bastante útil y muestra todos los campos.
    # No es necesario testearlo exhaustivamente a menos que lo personalices.
    # Solo nos aseguramos de que no falle y contenga lo esencial.
    assert "ForecastSystem" in repr(system)
    assert "id=1" in repr(system)
    assert "name='Sistema Z'" in repr(system)
    assert "contract_id=5" in repr(system)

def test_forecast_system_field_types():
    """
    Verifica que los tipos de campo son los esperados.
    Aunque dataclasses y type hints lo garantizan en gran medida, es una buena comprobación.
    """
    system = ForecastSystem(
        id=1,
        name="TestType",
        contract_id=10,
        port_id=20,
        hindcast_point_id=30
    )
    assert isinstance(system.id, int)
    assert isinstance(system.name, str)
    assert isinstance(system.contract_id, int)
    assert isinstance(system.port_id, int)
    assert isinstance(system.hindcast_point_id, int)

    system_partial = ForecastSystem(name="Partial")
    assert system_partial.id is None
    assert system_partial.contract_id is None
    assert system_partial.port_id is None
    assert system_partial.hindcast_point_id is None