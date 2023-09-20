from pydantic import BaseModel
from typing import Optional

class NewAccessPoint(BaseModel):
    ssid: str
    mac: str
    password: Optional[str] = None

class AccessPoint(BaseModel):
    bssid: str
    ssid: str
    frequency: int
    capabilities: str
    lasttime: int
    lastlat: float
    lastlon: float
    type: str
    bestlevel: int
    bestlat: float
    bestlon: float
    password: Optional[str] = None