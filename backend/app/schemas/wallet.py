from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class WalletBalanceBase(BaseModel):
    currency_type: str
    amount: float

class WalletBalance(WalletBalanceBase):
    id: int
    wallet_id: int

    class Config:
        from_attributes = True

class WalletBase(BaseModel):
    pass # balances are in relationships

class WalletCreate(WalletBase):
    user_id: int

class WalletUpdate(BaseModel):
    pass

class Wallet(WalletBase):
    id: int
    user_id: int
    updated_at: Optional[datetime] = None
    balances: List[WalletBalance] = []

    class Config:
        from_attributes = True
