from dataclasses import dataclass
from os import name

@dataclass
class Port:
    name: str
    country: str
    longitude: float 
    latitude: float 