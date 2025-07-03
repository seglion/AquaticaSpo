from typing import Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field # type: ignore
from pydantic import ConfigDict # type: ignore

class DownloadedDataBase(BaseModel):
    point_id: int = Field(..., gt=0)
    downloaded_at: datetime
    data: Dict  # JSON almacenado en diccionario

class DownloadedDataCreate(DownloadedDataBase):
    pass

class DownloadedDataUpdate(BaseModel):
    point_id: Optional[int] = Field(None, gt=0)
    downloaded_at: Optional[datetime] = None
    data: Optional[Dict] = None

class DownloadedDataRead(DownloadedDataBase):
    id: int

    model_config = ConfigDict(from_attributes=True)