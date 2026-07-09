"""Tests unitarios del cálculo de remonte (wave runup) EurOtop.

Cubren los dos regímenes del número de Iribarren (surging Ir<1.76 y no-surging
Ir>=1.76), la saturación del ángulo de ataque a 80 grados (incluyendo el cruce
0/360), un caso con marea negativa y la validación de longitudes.
"""

import numpy as np
import pytest

from app.shared.domain.remonte import calcular_remonte

_G = 9.81


def _iribarren(hs, tp, talud):
    """Recalcula el número de Iribarren de forma independiente a la función,
    para poder afirmar en qué régimen cae cada caso de test."""
    Tm = 0.8572 * np.asarray(tp, dtype=float)
    Lm = _G * Tm ** 2 / (2 * np.pi)
    return np.tan(np.arctan(talud)) / np.sqrt(np.asarray(hs, dtype=float) / Lm)


def test_regimen_surging_ir_menor_1_76():
    # talud=0.5, tp=6, hs=5 -> Ir ~ 1.44 (< 1.76): régimen surging.
    hs = np.array([5.0])
    tp = np.array([6.0])
    dir_oleaje = np.array([270.0])  # alineado con la perpendicular -> sigma_beta = 1
    marea = np.array([1.0])
    talud = 0.5
    perp = 270.0
    rugosidad = 1.0
    fs = 1.21

    ir = _iribarren(hs, tp, talud)
    assert ir[0] < 1.76  # confirmamos que estamos en el régimen surging

    res = calcular_remonte(
        hs=hs, tp=tp, dir_oleaje=dir_oleaje, marea=marea,
        talud=talud, angulo_perpendicular=perp, rugosidad=rugosidad,
        factor_seguridad=fs,
    )

    sigma = 1.0  # rugosidad * berma(1) * sigma_beta(1)
    esperado_ru2p = 1.65 * sigma * ir * hs
    esperado_ru1p = 1.45 * sigma * ir * hs

    np.testing.assert_allclose(res["ru2p"], esperado_ru2p)
    np.testing.assert_allclose(res["ru1p"], esperado_ru1p)
    np.testing.assert_allclose(res["cota_ru2p"], esperado_ru2p * fs + marea)
    np.testing.assert_allclose(res["cota_ru1p"], esperado_ru1p * fs + marea)


def test_regimen_no_surging_ir_mayor_igual_1_76():
    # talud=0.5, tp=6, hs=2 -> Ir ~ 2.27 (>= 1.76): régimen no-surging.
    hs = np.array([2.0])
    tp = np.array([6.0])
    dir_oleaje = np.array([270.0])
    marea = np.array([0.5])
    talud = 0.5
    perp = 270.0
    rugosidad = 1.0
    fs = 1.21

    ir = _iribarren(hs, tp, talud)
    assert ir[0] >= 1.76  # confirmamos el régimen no-surging

    res = calcular_remonte(
        hs=hs, tp=tp, dir_oleaje=dir_oleaje, marea=marea,
        talud=talud, angulo_perpendicular=perp, rugosidad=rugosidad,
        factor_seguridad=fs,
    )

    sigma = 1.0
    esperado_ru2p = 1.00 * sigma * (4.3 - 1.6 / np.sqrt(ir)) * hs
    esperado_ru1p = 1.00 * sigma * (5.1 - 4.48 / ir) * hs

    np.testing.assert_allclose(res["ru2p"], esperado_ru2p)
    np.testing.assert_allclose(res["ru1p"], esperado_ru1p)
    np.testing.assert_allclose(res["cota_ru2p"], esperado_ru2p * fs + marea)
    np.testing.assert_allclose(res["cota_ru1p"], esperado_ru1p * fs + marea)


def test_angulo_de_ataque_saturado_a_80():
    # Dos direcciones con desfase de 80 y 120 grados respecto a la perpendicular:
    # ambas saturan a 80 -> mismo sigma_beta -> mismo runup (con hs/tp idénticos).
    perp = 270.0
    hs = np.array([2.0, 2.0])
    tp = np.array([6.0, 6.0])
    dir_oleaje = np.array([190.0, 150.0])  # desfases de 80 y 120
    marea = np.array([0.0, 0.0])

    res = calcular_remonte(
        hs=hs, tp=tp, dir_oleaje=dir_oleaje, marea=marea,
        talud=0.5, angulo_perpendicular=perp, rugosidad=0.6,
    )

    # El runup del desfase de 120 (saturado a 80) coincide con el de 80.
    np.testing.assert_allclose(res["ru2p"][0], res["ru2p"][1])
    np.testing.assert_allclose(res["ru1p"][0], res["ru1p"][1])


def test_angulo_de_ataque_cruza_0_360():
    # perp=10, dir=350 -> el desfase envuelto es 20 (no 340). Debe coincidir con
    # perp=10, dir=30 (también 20 grados de desfase).
    hs = np.array([2.0])
    tp = np.array([6.0])
    marea = np.array([0.0])

    res_bajo = calcular_remonte(
        hs=hs, tp=tp, dir_oleaje=np.array([350.0]), marea=marea,
        talud=0.5, angulo_perpendicular=10.0, rugosidad=0.6,
    )
    res_alto = calcular_remonte(
        hs=hs, tp=tp, dir_oleaje=np.array([30.0]), marea=marea,
        talud=0.5, angulo_perpendicular=10.0, rugosidad=0.6,
    )

    np.testing.assert_allclose(res_bajo["ru2p"], res_alto["ru2p"])
    np.testing.assert_allclose(res_bajo["ru1p"], res_alto["ru1p"])


def test_marea_negativa_resta_de_la_cota():
    hs = np.array([2.0])
    tp = np.array([6.0])
    dir_oleaje = np.array([270.0])
    marea = np.array([-10.0])  # marea muy negativa -> cota puede quedar negativa
    fs = 1.21

    res = calcular_remonte(
        hs=hs, tp=tp, dir_oleaje=dir_oleaje, marea=marea,
        talud=0.5, angulo_perpendicular=270.0, rugosidad=1.0,
        factor_seguridad=fs,
    )

    # La cota es exactamente runup mayorado + marea (aquí, por debajo del runup).
    np.testing.assert_allclose(res["cota_ru2p"], res["ru2p"] * fs + marea)
    np.testing.assert_allclose(res["cota_ru1p"], res["ru1p"] * fs + marea)
    assert res["cota_ru2p"][0] < res["ru2p"][0]
    assert res["cota_ru2p"][0] < 0


def test_longitudes_distintas_lanzan_value_error():
    with pytest.raises(ValueError):
        calcular_remonte(
            hs=np.array([1.0, 2.0]),
            tp=np.array([6.0]),                 # longitud distinta
            dir_oleaje=np.array([270.0, 280.0]),
            marea=np.array([0.0, 0.0]),
            talud=0.5, angulo_perpendicular=270.0, rugosidad=0.6,
        )
