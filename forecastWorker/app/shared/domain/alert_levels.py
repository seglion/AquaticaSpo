import json
import os
from typing import Any, Dict, List, Optional


def _find_thresholds_file() -> str:
    """
    Localiza 'alert_thresholds.json'. En Docker se copia junto a main.py
    (mismo nivel que forecastWorker/), en desarrollo local vive en la raíz
    del repo, un nivel por encima de forecastWorker/.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "..", "..", "..", "alert_thresholds.json"),
        os.path.join(here, "..", "..", "..", "..", "alert_thresholds.json"),
    ]
    for candidate in candidates:
        candidate = os.path.normpath(candidate)
        if os.path.exists(candidate):
            return candidate
    raise FileNotFoundError(
        "No se encontró 'alert_thresholds.json' en ninguna de las rutas esperadas: "
        + ", ".join(os.path.normpath(c) for c in candidates)
    )


def _load_levels() -> List[Dict[str, Any]]:
    with open(_find_thresholds_file(), "r", encoding="utf-8") as f:
        config = json.load(f)
    return config["levels"]


_LEVELS = _load_levels()


def classify_wave_alert(height: Optional[float]) -> Dict[str, Any]:
    """
    Clasifica una altura de ola (Hs, en metros) según los tramos definidos
    en alert_thresholds.json, devolviendo {"level", "label", "color"}.
    """
    if height is None:
        height = 0.0

    for tier in _LEVELS:
        if tier["max"] is None or height < tier["max"]:
            return {
                "level": tier["level"],
                "label": tier["label"],
                "color": tier["color"],
            }

    # No debería alcanzarse: el último tramo siempre tiene max=None.
    last = _LEVELS[-1]
    return {"level": last["level"], "label": last["label"], "color": last["color"]}
