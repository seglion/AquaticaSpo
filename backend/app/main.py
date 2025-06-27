from fastapi import FastAPI
from app.api.routers import ports

app = FastAPI(title="Sistema de Previsión")

app.include_router(ports.router, prefix="/ports", tags=["ports"])