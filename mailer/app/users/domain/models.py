from dataclasses import dataclass


@dataclass
class User:
    id: int
    session_USER: str
    is_admin: bool
