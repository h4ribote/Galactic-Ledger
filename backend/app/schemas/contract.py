from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ContractBase(BaseModel):
    destination_planet_id: int
    item_id: int
    quantity: int
    currency_type: str = "CRED"
    reward_amount: float
    collateral_amount: float
    duration_seconds: int

class ContractCreate(ContractBase):
    origin_planet_id: int

class ContractResponse(ContractBase):
    id: int
    issuer_id: int
    contractor_id: Optional[int]
    origin_planet_id: int
    created_at: datetime
    accepted_at: Optional[datetime]
    deadline: Optional[datetime]
    status: str

    class Config:
        from_attributes = True
