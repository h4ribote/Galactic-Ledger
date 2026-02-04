from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WalletBase(BaseModel):
    balance: float

class WalletCreate(WalletBase):
    user_id: int

class WalletUpdate(BaseModel):
    balance: float

class Wallet(WalletBase):
    id: int
    user_id: int
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
