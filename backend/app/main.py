from fastapi import FastAPI
from app.ports.api.router import router as ports_router
from app.users.api.router import router as users_router
from app.contracts.api.router import router as contracts_router
from app.hindcastPoint.api.router import router as hindcast_router
from app.downloadData.api.router import router as download_data_router
from app.forecast_zones.api.router import router as forecast_zones_router
from app.forecastSystems.api.router import router as forecast_systems_router
from app.forecast_system_results.api.router import router as forecast_system_results_router
app = FastAPI(title="Ports Forecast API")

app.include_router(ports_router)
app.include_router(users_router)
app.include_router(contracts_router)
app.include_router(hindcast_router)
app.include_router(download_data_router)
app.include_router(forecast_zones_router)
app.include_router(forecast_systems_router)
app.include_router(forecast_system_results_router)