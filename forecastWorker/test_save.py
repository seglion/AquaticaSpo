import asyncio
import os
from dotenv import load_dotenv
from app.users.infrastructure.repositories import UserRepository
from app.forecastSystem.infrastructure.repositories import ForecastWorkerRepository
from app.forecastSystem.domain.models import ForecastZone

async def run():
    load_dotenv()
    user_repo = UserRepository()
    session = await user_repo.login(os.getenv("API_USER"), os.getenv("API_PASSWORD"))
    repo = ForecastWorkerRepository()
    
    # Simulating the first generated zone
    zones = [
        ForecastZone(id=1, forecast_system_id=1, name="Z1", description="D1", geom={"type": "Point", "coordinates": [0,0]})
    ]
    
    # Mock hypercube output
    mock_json = """
    {
        "ewam": {
            "timestamps": ["2025-07-06T22:00:00Z", "2025-07-06T23:00:00Z"],
            "zones": {
                "Z1": {
                    "Hs": [1.81, 1.95],
                    "Tp": [6.21, 6.35],
                    "PeakDirection": [270.5, 271.5]
                }
            }
        },
        "ncep_gfswave025": {
            "timestamps": ["2025-07-06T22:00:00Z", "2025-07-06T23:00:00Z"],
            "zones": {
                "Z1": {
                    "Hs": [1.75, 1.85],
                    "Tp": [6.1, 6.2],
                    "PeakDirection": [268, 269]
                }
            }
        }
    }
    """
    await repo.save_forecast_results(1, zones, mock_json, session)

asyncio.run(run())
