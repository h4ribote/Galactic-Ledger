from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc, func
from typing import List

from app.api import deps
from app.models.user import User
from app.models.market import MarketOrder
from app.schemas.market import MarketOrderCreate, MarketOrderResponse, OrderBookResponse, OrderBookEntry
from app.services import market as market_service

router = APIRouter()

@router.post("/", response_model=MarketOrderResponse)
async def create_order(
    order_in: MarketOrderCreate,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db)
):
    return await market_service.place_order(db, current_user.id, order_in)

@router.get("/", response_model=List[MarketOrderResponse])
async def read_my_orders(
    skip: int = 0,
    limit: int = 100,
    status: str = "OPEN",
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db)
):
    query = select(MarketOrder).where(
        MarketOrder.user_id == current_user.id,
        MarketOrder.status == status
    ).order_by(desc(MarketOrder.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.delete("/{id}", response_model=MarketOrderResponse)
async def cancel_order(
    id: int,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db)
):
    return await market_service.cancel_order(db, current_user.id, id)

@router.get("/book", response_model=OrderBookResponse)
async def get_order_book(
    planet_id: int,
    item_id: int,
    currency_type: str = "CRED",
    db: AsyncSession = Depends(deps.get_db)
):
    # Buy Orders (Bids): Price DESC
    buy_agg = select(MarketOrder.price, func.sum(MarketOrder.quantity - MarketOrder.filled_quantity).label("quantity")).where(
        MarketOrder.planet_id == planet_id,
        MarketOrder.item_id == item_id,
        MarketOrder.currency_type == currency_type,
        MarketOrder.order_type == "BUY",
        MarketOrder.status == "OPEN"
    ).group_by(MarketOrder.price).order_by(desc(MarketOrder.price))

    # Sell Orders (Asks): Price ASC
    sell_agg = select(MarketOrder.price, func.sum(MarketOrder.quantity - MarketOrder.filled_quantity).label("quantity")).where(
        MarketOrder.planet_id == planet_id,
        MarketOrder.item_id == item_id,
        MarketOrder.currency_type == currency_type,
        MarketOrder.order_type == "SELL",
        MarketOrder.status == "OPEN"
    ).group_by(MarketOrder.price).order_by(asc(MarketOrder.price))

    buy_res = await db.execute(buy_agg)
    sell_res = await db.execute(sell_agg)

    buy_orders = [OrderBookEntry(price=row.price, quantity=row.quantity) for row in buy_res.all()]
    sell_orders = [OrderBookEntry(price=row.price, quantity=row.quantity) for row in sell_res.all()]

    return OrderBookResponse(
        planet_id=planet_id,
        item_id=item_id,
        currency_type=currency_type,
        buy_orders=buy_orders,
        sell_orders=sell_orders
    )
