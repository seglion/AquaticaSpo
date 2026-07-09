from dataclasses import dataclass,field
from typing import Optional,List
from app.contracts.domain.models import Contract

@dataclass
class User:
    id: Optional[int]
    username: str
    email: str
    hashed_password: str
    is_admin: bool
    is_employee: bool
    contracts: List[Contract] = field(default_factory=list)