from typing import Optional
from datetime import date
from pydantic import BaseModel# type: ignore
from pydantic import ConfigDict# type: ignore


class ContractBase(BaseModel):
    name: str

    start_date: date
    end_date: Optional[date] = None
    active: bool = True

class ContractCreate(ContractBase):
    pass

class ContractUpdate(BaseModel):
    name: Optional[str] = None

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