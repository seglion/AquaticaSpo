"""Clasificación de niveles de alerta a partir de 'alert_thresholds.json', la
misma fuente de verdad que usan el frontend (wave-colors.ts) y forecastWorker
(app/shared/domain/alert_levels.py)."""

import json
import os
from typing import Any, Dict, List, Optional


def _find_thresholds_file() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "..", "..", "alert_thresholds.json"),
        os.path.join(here, "..", "..", "..", "alert_thresholds.json"),
    ]
    for candidate in candidates:
        candidate = os.path.normpath(candidate)
        if os.path.exists(candidate):
            return candidate
    raise FileNotFoundError(
        "No se encontró 'alert_thresholds.json' en ninguna de las rutas esperadas: "
        + ", ".join(os.path.normpath(c) for c in candidates)
    )


def _load_config() -> Dict[str, Any]:
    with open(_find_thresholds_file(), "r", encoding="utf-8") as f:
        return json.load(f)


_CONFIG = _load_config()
_WIND_LEVELS = _CONFIG.get("wind_levels", [])


def _classify(value: Optional[float], levels: List[Dict[str, Any]]) -> Dict[str, Any]:
    if value is None:
        value = 0.0
    for tier in levels:
        if tier["max"] is None or value < tier["max"]:
            return {
                "level": tier["level"],
                "label": tier["label"],
                "color": tier["color"],
            }
    last = levels[-1]
    return {"level": last["level"], "label": last["label"], "color": last["color"]}


def classify_wind_alert(speed: Optional[float]) -> Dict[str, Any]:
    return _classify(speed, _WIND_LEVELS)
