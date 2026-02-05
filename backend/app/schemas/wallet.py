from pydantic import BaseModel
from decimal import Decimal

class BalanceBase(BaseModel):
    currency_type: str
    amount: Decimal

class BalanceCreate(BalanceBase):
    user_id: int

class Balance(BalanceBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
