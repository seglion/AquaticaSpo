# app/forecast_zones/domain/test_models.py
import pytest
from app.forecast_zones.domain.models import ForecastZone

def test_forecast_zone_creation_minimal():
    """
    Comprueba la creación básica de una ForecastZone con los campos mínimos requeridos.
    """
    zone = ForecastZone(
        name="Zona Norte Galicia",
        description=None,
        forecast_system_id=1,
        geom={"type": "Point", "coordinates": [-8.72, 42.24]}
    )
    assert zone.name == "Zona Norte Galicia"
    assert zone.description is None
    assert zone.forecast_system_id == 1
    assert zone.geom == {"type": "Point", "coordinates": [-8.72, 42.24]}
    assert zone.id is None

def test_forecast_zone_creation_full():
    """
    Comprueba la creación de una ForecastZone con todos los campos, incluyendo ID y descripción.
    """
    zone = ForecastZone(
        id=5,
        name="Zona Cantábrico Este",
        description="Área de previsión para la costa vasca.",
        forecast_system_id=2,
        geom={"type": "Polygon", "coordinates": [[[0,0],[0,1],[1,1],[1,0],[0,0]]]}
    )
    assert zone.id == 5
    assert zone.name == "Zona Cantábrico Este"
    assert zone.description == "Área de previsión para la costa vasca."
    assert zone.forecast_system_id == 2
    assert zone.geom == {"type": "Polygon", "coordinates": [[[0,0],[0,1],[1,1],[1,0],[0,0]]]}

def test_forecast_system_id_type():
    """
    Asegura que forecast_system_id es un entero.
    """
    zone = ForecastZone(
        name="Punto Océano Atlántico",
        description=None,
        forecast_system_id=10,
        geom={"type": "Point", "coordinates": [-10.0, 45.0]}
    )
    assert isinstance(zone.forecast_system_id, int)
    assert zone.forecast_system_id == 10

def test_geom_is_dict():
    """
    Verifica que el campo geom acepta y mantiene un diccionario.
    """
    polygon_coords = {
        "type": "Polygon",
        "coordinates": [[
            [-7.5, 43.5], [-7.0, 43.5], [-7.0, 43.0], [-7.5, 43.0], [-7.5, 43.5]
        ]]
    }
    zone = ForecastZone(
        name="Polígono de Prueba",
        description="Un polígono para test",
        forecast_system_id=3,
        geom=polygon_coords
    )
    assert isinstance(zone.geom, dict)
    assert zone.geom == polygon_coords

def test_id_optional():
    """
    Comprueba que el ID es un campo opcional.
    """
    zone_without_id = ForecastZone(
        name="Zona sin ID",
        forecast_system_id=1,
        description=None,
        geom={"type": "Point", "coordinates": [0,0]}
    )
    assert zone_without_id.id is None

    zone_with_id = ForecastZone(
        id=99,
        name="Zona con ID",
        forecast_system_id=1,
        description=None,
        geom={"type": "Point", "coordinates": [0,0]}
    )
    assert zone_with_id.id == 99

def test_equality_of_forecast_zones():
    """
    Verifica que dos instancias de ForecastZone son iguales si tienen los mismos atributos, incluyendo el ID.
    """
    zone1 = ForecastZone(
        id=1,
        name="Zona A",
        description="Desc A",
        forecast_system_id=10,
        geom={"type": "Point", "coordinates": [1,1]}
    )
    zone2 = ForecastZone(
        id=1,
        name="Zona A",
        description="Desc A",
        forecast_system_id=10,
        geom={"type": "Point", "coordinates": [1,1]}
    )
    assert zone1 == zone2

def test_inequality_different_ids():
    """
    Verifica que dos instancias de ForecastZone son diferentes si tienen IDs distintos.
    """
    zone1 = ForecastZone(
        id=1,
        name="Zona A",
        description="Desc A",
        forecast_system_id=10,
        geom={"type": "Point", "coordinates": [1,1]}
    )
    zone2 = ForecastZone(
        id=2, # ID diferente
        name="Zona A",
        description="Desc A",
        forecast_system_id=10,
        geom={"type": "Point", "coordinates": [1,1]}
    )
    assert zone1 != zone2

def test_inequality_different_names():
    """
    Verifica la desigualdad cuando los nombres son diferentes.
    """
    zone1 = ForecastZone(
        id=1,
        name="Zona A",
        description="Desc A",
        forecast_system_id=10,
        geom={"type": "Point", "coordinates": [1,1]}
    )
    zone2 = ForecastZone(
        id=1,
        name="Zona B", # Nombre diferente
        description="Desc A",
        forecast_system_id=10,
        geom={"type": "Point", "coordinates": [1,1]}
    )
    assert zone1 != zone2

def test_inequality_different_forecast_system_id():
    """
    Verifica la desigualdad cuando el ID del sistema de previsión es diferente.
    """
    zone1 = ForecastZone(
        id=1,
        name="Zona A",
        description="Desc A",
        forecast_system_id=10,
        geom={"type": "Point", "coordinates": [1,1]}
    )
    zone2 = ForecastZone(
        id=1,
        name="Zona A",
        description="Desc A",
        forecast_system_id=11, # ID de sistema diferente
        geom={"type": "Point", "coordinates": [1,1]}
    )
    assert zone1 != zone2

def test_inequality_different_geom():
    """
    Verifica la desigualdad cuando la geometría es diferente.
    """
    zone1 = ForecastZone(
        id=1,
        name="Zona A",
        description="Desc A",
        forecast_system_id=10,
        geom={"type": "Point", "coordinates": [1,1]}
    )
    zone2 = ForecastZone(
        id=1,
        name="Zona A",
        description="Desc A",
        forecast_system_id=10,
        geom={"type": "Point", "coordinates": [2,2]} # Geometría diferente
    )
    assert zone1 != zone2