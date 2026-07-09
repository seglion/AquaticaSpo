from typing import Optional
from pydantic import BaseModel

class PortCreate(BaseModel):
    name: str
    country: str
    latitude: float
    longitude: float

class PortRead(PortCreate):
    id: int

    class Config:
        orm_mode = True

class PortUpdate(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None