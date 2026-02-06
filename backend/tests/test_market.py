import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from app.main import app
from app.db.session import SessionLocal, engine
from app.models.user import User
from app.models.planet import Planet
from app.models.item import Item
from app.models.inventory import Inventory
from app.models.wallet import Balance
from app.models.market import MarketOrder
from app.models.base import Base

# API prefix
API_PREFIX = "/api/v1"

# Setup DB for tests
@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_db():
    # Drop and Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield

@pytest.mark.asyncio
async def test_market_flow():
    # Use a custom AsyncClient pointing to test API
    async with AsyncClient(app=app, base_url="http://test") as ac:

        # 1. Setup Data (Users, Planet, Item)
        async with SessionLocal() as session:
            # Create Users
            user1 = User(id=101, username="Seller")
            user2 = User(id=102, username="Buyer")
            session.add_all([user1, user2])

            # Create Planet
            planet = Planet(name="MarketPlanet", x=0, y=0, slots=10)
            session.add(planet)

            # Create Item
            item = Item(name="Iron Ore", tier=1, volume=1)
            session.add(item)

            await session.commit()
            await session.refresh(user1)
            await session.refresh(user2)
            await session.refresh(planet)
            await session.refresh(item)

            user1_id = user1.id
            user2_id = user2.id
            planet_id = planet.id
            item_id = item.id

            # Give User1 Inventory (100 Iron)
            inv = Inventory(user_id=user1_id, planet_id=planet_id, item_id=item_id, quantity=100)
            session.add(inv)

            # Give User2 Money (1000 CRED)
            bal = Balance(user_id=user2_id, currency_type="CRED", amount=1000)
            session.add(bal)

            await session.commit()

        # 2. User1 places SELL Order (10 Iron @ 50 CRED)
        from app.api import deps

        async def mock_get_current_user_1():
            async with SessionLocal() as session:
                return await session.get(User, 101)

        async def mock_get_current_user_2():
            async with SessionLocal() as session:
                return await session.get(User, 102)

        app.dependency_overrides[deps.get_current_user] = mock_get_current_user_1

        sell_payload = {
            "planet_id": planet_id,
            "item_id": item_id,
            "order_type": "SELL",
            "currency_type": "CRED",
            "price": 50,
            "quantity": 10
        }
        res = await ac.post(f"{API_PREFIX}/market/", json=sell_payload)
        assert res.status_code == 200, res.text
        order_sell = res.json()
        assert order_sell["status"] == "OPEN"

        # Verify Inventory Deducted
        async with SessionLocal() as session:
            inv = await session.scalar(select(Inventory).where(
                Inventory.user_id==101,
                Inventory.planet_id==planet_id,
                Inventory.item_id==item_id
            ))
            assert inv.quantity == 90 # 100 - 10

        # 3. User2 places BUY Order (5 Iron @ 50 CRED) -> Should Match Immediately
        app.dependency_overrides[deps.get_current_user] = mock_get_current_user_2

        buy_payload = {
            "planet_id": planet_id,
            "item_id": item_id,
            "order_type": "BUY",
            "currency_type": "CRED",
            "price": 50,
            "quantity": 5
        }
        res = await ac.post(f"{API_PREFIX}/market/", json=buy_payload)
        assert res.status_code == 200, res.text
        order_buy = res.json()

        # Verify Match
        # Buy order should be FILLED
        assert order_buy["status"] == "FILLED"
        assert order_buy["filled_quantity"] == 5

        # Verify Sell order updated
        app.dependency_overrides[deps.get_current_user] = mock_get_current_user_1 # Switch back to seller
        res = await ac.get(f"{API_PREFIX}/market/")
        my_orders = res.json()
        found_sell = next(o for o in my_orders if o["id"] == order_sell["id"])
        assert found_sell["filled_quantity"] == 5
        assert found_sell["status"] == "OPEN" # Partial fill

        # Verify Balances/Inventories
        async with SessionLocal() as session:
            # User1 (Seller) has +250 CRED (5 * 50)
            bal1_amount = await session.scalar(select(Balance.amount).where(Balance.user_id==101))
            assert bal1_amount == 250

            # User2 (Buyer) has 1000 - 250 = 750 CRED
            bal2_amount = await session.scalar(select(Balance.amount).where(Balance.user_id==102))
            assert bal2_amount == 750

            # User2 has 5 Iron
            inv2_qty = await session.scalar(select(Inventory.quantity).where(
                Inventory.user_id==102,
                Inventory.planet_id==planet_id,
                Inventory.item_id==item_id
            ))
            assert inv2_qty == 5

        # 4. Cleanup Overrides
        app.dependency_overrides = {}
