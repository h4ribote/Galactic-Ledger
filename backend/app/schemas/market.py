from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class MarketOrderBase(BaseModel):
    planet_id: int
    item_id: int
    order_type: str # 'BUY', 'SELL'
    currency_type: Optional[str] = "CRED"
    price: Decimal
    quantity: int

class MarketOrderCreate(MarketOrderBase):
    pass

class MarketOrderResponse(MarketOrderBase):
    id: int
    user_id: int
    filled_quantity: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class OrderBookEntry(BaseModel):
    price: Decimal
    quantity: int

class OrderBookResponse(BaseModel):
    planet_id: int
    item_id: int
    currency_type: str
    buy_orders: List[OrderBookEntry]
    sell_orders: List[OrderBookEntry]
