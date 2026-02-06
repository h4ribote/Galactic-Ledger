import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, asc
from fastapi import HTTPException
from decimal import Decimal
from typing import List, Optional
from datetime import datetime, timezone

from app.models.market import MarketOrder
from app.models.wallet import Balance
from app.models.inventory import Inventory
from app.models.item import Item
from app.models.planet import Planet
from app.schemas.market import MarketOrderCreate

logger = logging.getLogger(__name__)

async def get_or_create_balance(db: AsyncSession, user_id: int, currency_type: str, for_update: bool = False) -> Balance:
    query = select(Balance).where(
        Balance.user_id == user_id,
        Balance.currency_type == currency_type
    )
    if for_update:
        query = query.with_for_update()

    result = await db.execute(query)
    balance = result.scalars().first()
    if not balance:
        balance = Balance(user_id=user_id, currency_type=currency_type, amount=0)
        db.add(balance)
        # Ensure row exists so it can be locked (implicit lock on insert until commit)
        await db.flush()
    return balance

async def get_or_create_inventory(db: AsyncSession, user_id: int, planet_id: int, item_id: int, for_update: bool = False) -> Inventory:
    query = select(Inventory).where(
        Inventory.user_id == user_id,
        Inventory.planet_id == planet_id,
        Inventory.item_id == item_id
    )
    if for_update:
        query = query.with_for_update()

    result = await db.execute(query)
    inventory = result.scalars().first()
    if not inventory:
        inventory = Inventory(user_id=user_id, planet_id=planet_id, item_id=item_id, quantity=0)
        db.add(inventory)
        await db.flush()
    return inventory


async def match_orders(db: AsyncSession, taker_order: MarketOrder):
    """
    Matches the taker_order against existing maker orders in the book.
    Updates balances, inventories, and order statuses.
    """

    # Refresh to ensure we have latest status
    await db.refresh(taker_order)

    while taker_order.status == "OPEN" and taker_order.quantity > taker_order.filled_quantity:
        remaining_qty = taker_order.quantity - taker_order.filled_quantity

        # Find Maker Order
        if taker_order.order_type == "BUY":
            # Looking for SELL orders with price <= taker.price
            # Best price first (Lowest SELL price), then oldest
            query = select(MarketOrder).where(
                MarketOrder.planet_id == taker_order.planet_id,
                MarketOrder.item_id == taker_order.item_id,
                MarketOrder.currency_type == taker_order.currency_type,
                MarketOrder.order_type == "SELL",
                MarketOrder.status == "OPEN",
                MarketOrder.price <= taker_order.price
            ).order_by(asc(MarketOrder.price), asc(MarketOrder.created_at))

        else: # SELL
            # Looking for BUY orders with price >= taker.price
            # Best price first (Highest BUY price), then oldest
            query = select(MarketOrder).where(
                MarketOrder.planet_id == taker_order.planet_id,
                MarketOrder.item_id == taker_order.item_id,
                MarketOrder.currency_type == taker_order.currency_type,
                MarketOrder.order_type == "BUY",
                MarketOrder.status == "OPEN",
                MarketOrder.price >= taker_order.price
            ).order_by(desc(MarketOrder.price), asc(MarketOrder.created_at))

        # Lock maker order
        result = await db.execute(query.limit(1).with_for_update())
        maker_order = result.scalars().first()

        if not maker_order:
            break # No match found

        # Match found!
        match_price = maker_order.price # Execute at Maker's price
        match_qty = min(remaining_qty, maker_order.quantity - maker_order.filled_quantity)

        # Update Orders
        taker_order.filled_quantity += match_qty
        maker_order.filled_quantity += match_qty

        if taker_order.filled_quantity == taker_order.quantity:
            taker_order.status = "FILLED"

        if maker_order.filled_quantity == maker_order.quantity:
            maker_order.status = "FILLED"

        db.add(taker_order)
        db.add(maker_order)

        # Identify Buyer and Seller
        if maker_order.order_type == "SELL":
            seller_id = maker_order.user_id
            buyer_id = taker_order.user_id
        else:
            seller_id = taker_order.user_id
            buyer_id = maker_order.user_id

        # Transfer Assets
        # 1. Seller receives Money (match_qty * match_price)
        seller_balance = await get_or_create_balance(db, seller_id, taker_order.currency_type, for_update=True)
        seller_balance.amount += Decimal(match_qty) * match_price
        db.add(seller_balance)

        # 2. Buyer receives Items (match_qty)
        # Buyer gets items at the location of the market (planet_id)
        buyer_inventory = await get_or_create_inventory(db, buyer_id, taker_order.planet_id, taker_order.item_id, for_update=True)
        buyer_inventory.quantity += match_qty
        db.add(buyer_inventory)

        # 3. Refund Logic for Taker Buyer
        # If Taker is Buyer and paid `taker.price` but matched at `match_price` < `taker.price`.
        # Refund = (taker.price - match_price) * match_qty
        if taker_order.order_type == "BUY" and taker_order.price > match_price:
            refund = (taker_order.price - match_price) * Decimal(match_qty)
            if refund > 0:
                buyer_balance = await get_or_create_balance(db, buyer_id, taker_order.currency_type, for_update=True)
                buyer_balance.amount += refund
                db.add(buyer_balance)

        # Commit this trade
        await db.commit()


async def place_order(db: AsyncSession, user_id: int, order_in: MarketOrderCreate) -> MarketOrder:
    # Validate Inputs
    # Check Planet
    planet = await db.get(Planet, order_in.planet_id)
    if not planet:
        raise HTTPException(status_code=404, detail="Planet not found")

    # Check Item
    item = await db.get(Item, order_in.item_id)
    if not item:
         raise HTTPException(status_code=404, detail="Item not found")

    # Locking resources
    if order_in.order_type == "BUY":
        # Buyer needs Money
        total_cost = order_in.price * order_in.quantity
        balance = await get_or_create_balance(db, user_id, order_in.currency_type, for_update=True)
        if balance.amount < total_cost:
            raise HTTPException(status_code=400, detail=f"Insufficient funds ({order_in.currency_type})")

        balance.amount -= total_cost
        db.add(balance)

    elif order_in.order_type == "SELL":
        # Seller needs Items at that planet
        query = select(Inventory).where(
            Inventory.user_id == user_id,
            Inventory.planet_id == order_in.planet_id,
            Inventory.item_id == order_in.item_id
        ).with_for_update()

        inventory = await db.scalar(query)
        if not inventory or inventory.quantity < order_in.quantity:
            raise HTTPException(status_code=400, detail="Insufficient items in inventory at this location")

        inventory.quantity -= order_in.quantity
        db.add(inventory)

    else:
        raise HTTPException(status_code=400, detail="Invalid order type")

    # Create Order
    order = MarketOrder(
        user_id=user_id,
        planet_id=order_in.planet_id,
        item_id=order_in.item_id,
        order_type=order_in.order_type,
        currency_type=order_in.currency_type,
        price=order_in.price,
        quantity=order_in.quantity,
        filled_quantity=0,
        status="OPEN"
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    # Trigger Matching
    try:
        await match_orders(db, order)
    except Exception as e:
        # If matching fails, we should probably not fail the order placement itself?
        # But for now, let's raise so we know.
        # In production, matching might be async task.
        logger.error(f"Error during matching: {e}")
        raise e

    await db.refresh(order)
    return order

async def cancel_order(db: AsyncSession, user_id: int, order_id: int) -> MarketOrder:
    # Need lock on order to update status
    # .with_for_update() is good.
    result = await db.execute(select(MarketOrder).where(MarketOrder.id == order_id).with_for_update())
    order = result.scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if order.status != "OPEN":
        raise HTTPException(status_code=400, detail="Order cannot be cancelled")

    remaining_qty = order.quantity - order.filled_quantity

    if remaining_qty > 0:
        # Refund Locked Resources
        if order.order_type == "BUY":
            # Refund Money
            refund_amount = Decimal(remaining_qty) * order.price
            balance = await get_or_create_balance(db, user_id, order.currency_type, for_update=True)
            balance.amount += refund_amount
            db.add(balance)
        else: # SELL
            # Refund Items
            inventory = await get_or_create_inventory(db, user_id, order.planet_id, order.item_id, for_update=True)
            inventory.quantity += remaining_qty
            db.add(inventory)

    order.status = "CANCELLED"
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order
