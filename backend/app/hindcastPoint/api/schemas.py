# app/hindcastPoint/api/schemas.py

from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic import ConfigDict

class HindcastPointBase(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    url: str
    models: Optional[List[str]] = None


class HindcastPointCreate(HindcastPointBase):
    pass


class HindcastPointUpdate(BaseModel):
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    url: Optional[str] = None
    models: Optional[List[str]] = None


class HindcastPointRead(HindcastPointBase):
    id: int

    model_config = ConfigDict(from_attributes=True)