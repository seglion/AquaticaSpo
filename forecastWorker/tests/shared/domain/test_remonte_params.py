"""Tests de la resolución de parámetros de remonte por zona.

Cubren la función pura ``resolve_zone_params``: prioridad del override por id,
respaldo por nombre, zona sin entrada (cae al default), override parcial y
error si falta alguna clave requerida.
"""

import pytest

from app.shared.domain.remonte_params import resolve_zone_params

_CONFIG = {
    "default": {
        "talud": 0.5,
        "angulo_perpendicular": 0.0,
        "rugosidad": 1.0,
        "berma": 1.0,
        "factor_seguridad": 1.21,
    },
    "zones": {
        "1": {"angulo_perpendicular": 290.0, "rugosidad": 0.55, "talud": 0.4},
        "Muelle Norte": {"rugosidad": 0.7},
    },
}


def test_override_por_id_tiene_prioridad_y_fusiona_sobre_default():
    params = resolve_zone_params(_CONFIG, zone_id=1, zone_name="cualquiera")
    assert params["angulo_perpendicular"] == 290.0
    assert params["rugosidad"] == 0.55
    assert params["talud"] == 0.4
    # No sobreescritos por el override -> vienen del default.
    assert params["berma"] == 1.0
    assert params["factor_seguridad"] == 1.21


def test_respaldo_por_nombre_cuando_no_hay_match_por_id():
    # id sin entrada, pero el nombre sí está en la config.
    params = resolve_zone_params(_CONFIG, zone_id=999, zone_name="Muelle Norte")
    assert params["rugosidad"] == 0.7  # del override por nombre
    assert params["talud"] == 0.5      # resto, del default


def test_zona_sin_entrada_devuelve_default_completo():
    params = resolve_zone_params(_CONFIG, zone_id=42, zone_name="Desconocida")
    assert params == {
        "talud": 0.5,
        "angulo_perpendicular": 0.0,
        "rugosidad": 1.0,
        "berma": 1.0,
        "factor_seguridad": 1.21,
    }


def test_override_parcial_resto_cae_al_default():
    params = resolve_zone_params(_CONFIG, zone_id=None, zone_name="Muelle Norte")
    # Solo 'rugosidad' está en el override; el resto es el default.
    assert params["rugosidad"] == 0.7
    assert params["talud"] == 0.5
    assert params["angulo_perpendicular"] == 0.0
    assert params["berma"] == 1.0
    assert params["factor_seguridad"] == 1.21


def test_resultado_siempre_trae_las_cinco_claves():
    params = resolve_zone_params(_CONFIG, zone_id=1, zone_name=None)
    assert set(params.keys()) == {
        "talud", "angulo_perpendicular", "rugosidad", "berma", "factor_seguridad",
    }


def test_falta_una_clave_lanza_value_error():
    config_incompleto = {"default": {"talud": 0.5}, "zones": {}}
    with pytest.raises(ValueError):
        resolve_zone_params(config_incompleto, zone_id=1, zone_name="Z")
