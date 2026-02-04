from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class PlanetBase(BaseModel):
    name: str
    x: float
    y: float
    slots: int
    temperature: float
    gravity: float

class PlanetCreate(PlanetBase):
    pass

class PlanetUpdate(BaseModel):
    name: Optional[str] = None
    owner_id: Optional[int] = None

class Planet(PlanetBase):
    id: int
    owner_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
