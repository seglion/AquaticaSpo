from dataclasses import dataclass

@dataclass
class User:
    id: int
    username: str
    email: str
    hashed_password: str
    is_admin: bool
    is_employee: bool