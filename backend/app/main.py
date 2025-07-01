from fastapi import FastAPI
from app.ports.api.router import router as ports_router
from app.users.api.router import router as users_router
app = FastAPI(title="Ports Forecast API")

app.include_router(ports_router)  
app.include_router(users_router) 