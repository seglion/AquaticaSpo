from fastapi import FastAPI
from app.ports.api.router import router as ports_router

app = FastAPI(title="Ports Forecast API")

app.include_router(ports_router)  