from dataclasses import dataclass
from typing import Optional
@dataclass
class User:
    id: Optional[int]
    username: str
    email: str
    hashed_password: str
    is_admin: bool
    is_employee: bool