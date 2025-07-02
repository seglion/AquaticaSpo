from typing import Optional
from datetime import date
from pydantic import BaseModel
from pydantic import ConfigDict


class ContractBase(BaseModel):
    name: str
    forecast_system_id: int
    start_date: date
    end_date: Optional[date] = None
    active: bool = True

class ContractCreate(ContractBase):
    pass

class ContractUpdate(BaseModel):
    name: Optional[str] = None
    forecast_system_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    active: Optional[bool] = None
    
class ContractOut(ContractBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
    
    
class ContractToUserBase(BaseModel):
    contract_id: int
    user_id: int
    
class RemoveContractFromUserBase(BaseModel):
    contract_id: int
    user_id: int