"""Cálculo del remonte (wave runup) del oleaje sobre un talud liso.

Implementa las fórmulas empíricas del manual **EurOtop/TAW** para el runup
estadístico Ru2% (superado por el 2% de las olas) y Ru1% (superado por el 1%)
sobre taludes lisos, rugosos e impermeables.

Notas de modelización:
- El periodo espectral Tm-1,0 se **estima** como ``0.8572 * Tp``, ya que en este
  sistema no se dispone del periodo espectral real (solo del periodo de pico Tp).
- El factor de berma (``sigma_b``) se trata como un parámetro simple con valor
  por defecto 1.0. **No** se da soporte a bermas reales (curvas B/Lberm) ni a
  taludes compuestos, igual que en el pipeline MATLAB de origen.

El origen de esta lógica es un pipeline de previsión de oleaje para obra
portuaria: el oleaje ya propagado a pie de talud (Hs, Tp, dirección) y la marea
prevista se combinan para obtener la cota de remonte, que luego se compara contra
límites por punto para generar un semáforo de alerta. Aquí solo se traslada el
cálculo del remonte en sí.
"""

from typing import Dict

import numpy as np

# Umbral del número de Iribarren que separa el régimen "surging" (Ir < 1.76) del
# régimen no-surging en las fórmulas de runup de EurOtop.
_IRIBARREN_SURGING = 1.76

# Aceleración de la gravedad [m/s^2].
_G = 9.81


def calcular_remonte(
    hs: np.ndarray,              # altura de ola significante en el pie del talud [m], por timestep
    tp: np.ndarray,              # periodo de pico [s], por timestep
    dir_oleaje: np.ndarray,      # dirección de procedencia del oleaje [grados, 0-360, convención geográfica]
    marea: np.ndarray,           # nivel de marea [m], por timestep (mismo índice temporal que hs/tp/dir)
    talud: float,                # pendiente del talud, ej. 1/2 (V/H)
    angulo_perpendicular: float, # orientación de la perpendicular a la estructura [grados]
    rugosidad: float,            # factor de rugosidad del talud, sigma_f (adimensional, típicamente 0.4-1.0)
    berma: float = 1.0,          # factor de reducción por berma, sigma_b (1.0 si no hay berma)
    factor_seguridad: float = 1.21,  # mayoración aplicada al runup teórico antes de sumar la marea
) -> Dict[str, np.ndarray]:
    """Calcula el remonte Ru2% y Ru1% y sus cotas (runup + marea) por timestep.

    Todas las entradas de serie temporal (``hs``, ``tp``, ``dir_oleaje``,
    ``marea``) deben tener la misma longitud y compartir el mismo índice
    temporal. El cálculo es completamente vectorizado con numpy.

    Devuelve un diccionario con cuatro arrays de la misma longitud que las
    entradas:

    - ``ru2p``: runup Ru2% teórico [m].
    - ``ru1p``: runup Ru1% teórico [m].
    - ``cota_ru2p``: cota de remonte del 2% = ``ru2p * factor_seguridad + marea`` [m].
    - ``cota_ru1p``: cota de remonte del 1% = ``ru1p * factor_seguridad + marea`` [m].

    Raises:
        ValueError: si ``hs``, ``tp``, ``dir_oleaje`` y ``marea`` no tienen la
            misma longitud.
    """
    hs = np.asarray(hs, dtype=float)
    tp = np.asarray(tp, dtype=float)
    dir_oleaje = np.asarray(dir_oleaje, dtype=float)
    marea = np.asarray(marea, dtype=float)

    # 1. Validar que todas las series temporales comparten longitud.
    longitudes = {
        "hs": hs.shape[0],
        "tp": tp.shape[0],
        "dir_oleaje": dir_oleaje.shape[0],
        "marea": marea.shape[0],
    }
    if len(set(longitudes.values())) != 1:
        raise ValueError(
            "hs, tp, dir_oleaje y marea deben tener la misma longitud; "
            f"se recibieron {longitudes}."
        )

    # 2. Ángulo del talud.
    beta = np.arctan(talud)

    # 3. Periodo espectral estimado y longitud de onda en aguas profundas.
    #    Tm-1,0 se aproxima como 0.8572*Tp (no se dispone del espectral real).
    Tm_menos1_0 = 0.8572 * tp
    Lm_menos1_0 = _G * Tm_menos1_0 ** 2 / (2 * np.pi)

    # 4. Número de Iribarren (surf similarity), calculado con Tm-1,0.
    Ir = np.tan(beta) / np.sqrt(hs / Lm_menos1_0)

    # 5. Ángulo de ataque del oleaje respecto a la perpendicular de la estructura.
    #    Se envuelve la diferencia a [-180, 180] para evitar la discontinuidad en
    #    0/360 (p.ej. perp=10, dir=350 -> ataque de 20, no de 340) y se satura a 80.
    diff = (angulo_perpendicular - dir_oleaje + 180.0) % 360.0 - 180.0
    angulo_ataque = np.abs(diff)
    angulo_ataque_sat = np.minimum(angulo_ataque, 80.0)
    sigma_beta = 1 - 0.0022 * angulo_ataque_sat

    # 6. Factor de reducción combinado (rugosidad * berma * oblicuidad).
    sigma = rugosidad * berma * sigma_beta

    # 7. Runup Ru2% y Ru1% según régimen surging (Ir < 1.76) o no.
    #    Nota de borde: con hs == 0 (zonas de sombra que la propagación fija a 0)
    #    Ir -> inf; np.where selecciona la rama no-surging y el resultado es 0,
    #    aunque numpy puede emitir un RuntimeWarning por la rama surging (inf*0).
    Ru2p = np.where(
        Ir < _IRIBARREN_SURGING,
        1.65 * sigma * Ir * hs,
        1.00 * sigma * (4.3 - 1.6 / np.sqrt(Ir)) * hs,
    )
    Ru1p = np.where(
        Ir < _IRIBARREN_SURGING,
        1.45 * sigma * Ir * hs,
        1.00 * sigma * (5.1 - 4.48 / Ir) * hs,
    )

    # 8. Cota final de remonte: mayorar el runup teórico y sumar el nivel de marea.
    cota_ru2p = Ru2p * factor_seguridad + marea
    cota_ru1p = Ru1p * factor_seguridad + marea

    return {
        "ru2p": Ru2p,
        "ru1p": Ru1p,
        "cota_ru2p": cota_ru2p,
        "cota_ru1p": cota_ru1p,
    }
