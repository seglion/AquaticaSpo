from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any 
@dataclass
class ForecastSystemResult:
    """
    Representa un resultado de previsión para una zona específica.
    El campo 'result_data' contendrá un JSON cuya estructura varía
    dependiendo de si la zona es un punto o un área.
    """
    id: Optional[int]
    forecast_zone_id: int
    execution_date: datetime
    result_data: Any # Será un diccionario que mapea al JSONB de la BDit