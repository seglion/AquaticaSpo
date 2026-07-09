"""Carga de los parámetros de remonte (wave runup) por zona.

Los parámetros estructurales que necesita ``calcular_remonte`` (talud, ángulo
perpendicular de la estructura, rugosidad, berma y factor de seguridad) no viven
en la base de datos ni viajan en el payload de zona: se resuelven aquí desde el
fichero ``remonte_params.json``, una única fuente de verdad al estilo de
``alert_thresholds.json``.

El fichero tiene un bloque ``default`` y overrides por zona (clave = id de zona en
string, con respaldo por nombre)::

    {
      "default": {"talud": 0.5, "angulo_perpendicular": 0.0, "rugosidad": 1.0,
                   "berma": 1.0, "factor_seguridad": 1.21},
      "zones": {"1": {"angulo_perpendicular": 290.0, "rugosidad": 0.55}}
    }

Cada override se fusiona sobre el ``default``, así que puede ser parcial.
"""

import json
import os
from typing import Any, Dict, Optional

# Claves que ``calcular_remonte`` espera; el resultado resuelto siempre las trae.
_PARAM_KEYS = ("talud", "angulo_perpendicular", "rugosidad", "berma", "factor_seguridad")


def _find_params_file() -> str:
    """
    Localiza 'remonte_params.json'. En Docker se copia junto a main.py (mismo
    nivel que forecastWorker/), en desarrollo local vive en la raíz del repo, un
    nivel por encima de forecastWorker/. Mismas rutas candidatas que
    alert_levels._find_thresholds_file.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "..", "..", "..", "remonte_params.json"),
        os.path.join(here, "..", "..", "..", "..", "remonte_params.json"),
    ]
    for candidate in candidates:
        candidate = os.path.normpath(candidate)
        if os.path.exists(candidate):
            return candidate
    raise FileNotFoundError(
        "No se encontró 'remonte_params.json' en ninguna de las rutas esperadas: "
        + ", ".join(os.path.normpath(c) for c in candidates)
    )


def _load_config() -> Dict[str, Any]:
    with open(_find_params_file(), "r", encoding="utf-8") as f:
        return json.load(f)


_CONFIG = _load_config()


def resolve_zone_params(
    config: Dict[str, Any],
    zone_id: Optional[int],
    zone_name: Optional[str],
) -> Dict[str, float]:
    """Fusiona el bloque ``default`` con el override de la zona.

    Busca el override primero por ``str(zone_id)`` y, si no lo encuentra, por
    ``zone_name``. Devuelve siempre las cinco claves de ``_PARAM_KEYS``; si el
    override es parcial, el resto cae al ``default``. Función pura (sin I/O) para
    poder testearla con configuraciones en memoria.
    """
    resolved: Dict[str, float] = dict(config.get("default", {}))

    zones = config.get("zones", {})
    override = None
    if zone_id is not None:
        override = zones.get(str(zone_id))
    if override is None and zone_name is not None:
        override = zones.get(zone_name)

    if override:
        resolved.update(override)

    faltantes = [k for k in _PARAM_KEYS if k not in resolved]
    if faltantes:
        raise ValueError(
            "Faltan parámetros de remonte para la zona "
            f"(id={zone_id}, name={zone_name!r}): {faltantes}. "
            "Deben estar en el bloque 'default' o en el override de la zona."
        )

    return {k: resolved[k] for k in _PARAM_KEYS}


def get_zone_remonte_params(
    zone_id: Optional[int],
    zone_name: Optional[str],
) -> Dict[str, float]:
    """Parámetros de remonte resueltos para una zona, desde el fichero de config."""
    return resolve_zone_params(_CONFIG, zone_id, zone_name)
