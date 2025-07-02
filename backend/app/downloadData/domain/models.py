# app/downloadedData/domain/models.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any


@dataclass
class DownloadedData:
    """Modelo que representa una descarga de datos para un punto Hindcast."""
    point_id: int
    downloaded_at: datetime
    data: Any  # JSON almacenado como diccionario
    id: Optional[int] = None  # El ID se asigna al guardarlo en la base de datos