import pytest
from app.hindcastPoint.domain.models import HindcastPoint

def test_hindcast_point_creation_minimal():
    hp = HindcastPoint(latitude=42.0, longitude=-3.0, url="http://data.source")
    assert hp.latitude == 42.0
    assert hp.longitude == -3.0
    assert hp.url == "http://data.source"
    assert hp.models is None
    assert hp.id is None  # id no se asigna en constructor

def test_hindcast_point_with_models():
    models_list = ["modelA", "modelB"]
    hp = HindcastPoint(latitude=10.0, longitude=20.0, url="http://data.source", models=models_list)
    assert hp.models == models_list
    assert isinstance(hp.models, list)
    assert all(isinstance(m, str) for m in hp.models)

def test_hindcast_point_id_field_is_not_settable_in_constructor():
    hp = HindcastPoint(latitude=1.0, longitude=2.0, url="url")
    with pytest.raises(TypeError):
        # Intentar pasar id en constructor debe fallar
        HindcastPoint(latitude=1.0, longitude=2.0, url="url", id=123)

def test_hindcast_point_id_can_be_set_manually():
    hp = HindcastPoint(latitude=1.0, longitude=2.0, url="url")
    hp.id = 99
    assert hp.id == 99