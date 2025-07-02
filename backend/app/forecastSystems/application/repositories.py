
from app.forecastSystems.domain.models import ForecastSystem

class ForecastSystemRepositoryABC:
    async def create_forecastSystem(self, forecastSystem: ForecastSystem) -> ForecastSystem:
        ...