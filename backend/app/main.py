from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import traceback
from fastapi.middleware.cors import CORSMiddleware

from app.ports.api.router import router as ports_router
from app.users.api.router import router as users_router
from app.contracts.api.router import router as contracts_router
from app.hindcastPoint.api.router import router as hindcast_router
from app.downloadData.api.router import router as download_data_router
from app.forecast_zones.api.router import router as forecast_zones_router
from app.forecastSystems.api.router import router as forecast_systems_router
from app.forecast_system_results.api.router import router as forecast_system_results_router
from app.shared.config import settings

app = FastAPI(title="Ports Forecast API")

@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        print("UNHANDLED EXCEPTION:")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "details": str(e)})

# Orígenes permitidos por CORS, configurables por entorno (ALLOWED_ORIGINS en el .env).
# Por defecto cubre el frontend local; en producción se añade https://spo.aquatica.gal.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ports_router)
app.include_router(users_router)
app.include_router(contracts_router)
app.include_router(hindcast_router)
app.include_router(download_data_router)
app.include_router(forecast_zones_router)
app.include_router(forecast_systems_router)
app.include_router(forecast_system_results_router)