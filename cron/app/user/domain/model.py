

from dataclasses import dataclass



@dataclass  # noqa: D101

class User:
    id: int
    session_USER: str
    is_admin: bool 
    