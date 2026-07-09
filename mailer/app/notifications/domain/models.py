from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Recipient:
    id: int
    username: str
    email: str
    is_admin: bool
    is_employee: bool


@dataclass
class AlertInterval:
    """Tramo de horas consecutivas con el mismo nivel de alerta, para el modelo
    de referencia (EWAM) de una zona."""
    alert_level: Optional[str]
    alert_label: Optional[str]
    alert_color: Optional[str]
    start_time: Optional[str]
    end_time: Optional[str]
    max_hs: Optional[float]


@dataclass
class ZoneAlert:
    zone_id: Optional[int]
    zone_name: Optional[str]
    max_hs: Optional[float]
    alert_level: Optional[str]
    alert_label: Optional[str]
    alert_color: Optional[str]
    model: Optional[str]
    peak_time: Optional[str]
    lon: Optional[float] = None
    lat: Optional[float] = None
    intervals: List[AlertInterval] = field(default_factory=list)


# Orden de severidad para ordenar las zonas peor-alerta-primero en el email.
_SEVERITY_ORDER = {"red": 0, "orange": 1, "yellow": 2, None: 3}


@dataclass
class ForecastCompletedEvent:
    forecast_system_id: int
    forecast_system_name: Optional[str]
    contract_id: Optional[int]
    executed_at: str
    zones: List[ZoneAlert] = field(default_factory=list)

    def zones_by_severity(self) -> List[ZoneAlert]:
        return sorted(self.zones, key=lambda z: _SEVERITY_ORDER.get(z.alert_level, 99))

    @classmethod
    def from_message(cls, message: dict) -> "ForecastCompletedEvent":
        zones = []
        for z in message.get("zones", []):
            z = dict(z)
            intervals = [AlertInterval(**iv) for iv in z.pop("intervals", [])]
            zones.append(ZoneAlert(**z, intervals=intervals))
        return cls(
            forecast_system_id=message["forecast_system_id"],
            forecast_system_name=message.get("forecast_system_name"),
            contract_id=message.get("contract_id"),
            executed_at=message.get("executed_at"),
            zones=zones,
        )


@dataclass
class ForecastFailedEvent:
    forecast_system_id: int
    forecast_system_name: Optional[str]
    contract_id: Optional[int]
    failed_at: str
    error_message: str

    @classmethod
    def from_message(cls, message: dict) -> "ForecastFailedEvent":
        return cls(
            forecast_system_id=message["forecast_system_id"],
            forecast_system_name=message.get("forecast_system_name"),
            contract_id=message.get("contract_id"),
            failed_at=message.get("failed_at"),
            error_message=message.get("error_message", "Error desconocido"),
        )
