import pytest
from httpx import AsyncClient
from sqlalchemy import select, delete
from app.main import app
from app.db.session import SessionLocal
from app.api.endpoints.users import get_current_user
from app.models.user import User
from app.models.planet import Planet
from app.models.wallet import Balance
from app.models.item import Item
from app.models.inventory import Inventory
from app.models.building import Building
from decimal import Decimal

# We need to make sure we use a test user
TEST_USER_ID = 999
TEST_PLANET_ID = 999
TEST_ITEM_ID = 999
TEST_ITEM_NAME = "Iron" # Matches game data

async def override_get_current_user():
    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.id == TEST_USER_ID))
        user = result.scalars().first()
        if not user:
             # Create on the fly if missing (should be setup by test, but safety net)
             user = User(id=TEST_USER_ID, discord_id="test_auth_user", username="TestAuthUser")
             session.add(user)
             await session.commit()
             await session.refresh(user)
        return user

app.dependency_overrides[get_current_user] = override_get_current_user

@pytest.mark.asyncio
async def test_build_structure():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        async with SessionLocal() as session:
            # CLEANUP
            await session.execute(delete(Building).where(Building.planet_id == TEST_PLANET_ID))
            await session.execute(delete(Inventory).where(Inventory.planet_id == TEST_PLANET_ID))
            await session.execute(delete(Planet).where(Planet.id == TEST_PLANET_ID))
            await session.execute(delete(Balance).where(Balance.user_id == TEST_USER_ID))
            await session.execute(delete(User).where(User.id == TEST_USER_ID))
            # Don't delete Item if it's shared, but we can ensure it exists

            await session.commit()

            # SETUP
            user = User(id=TEST_USER_ID, discord_id="test_builder", username="Builder")
            session.add(user)

            balance = Balance(user_id=TEST_USER_ID, currency_type="CRED", amount=Decimal(500))
            session.add(balance)

            planet = Planet(id=TEST_PLANET_ID, name="BuildWorld", x=10, y=10, owner_id=TEST_USER_ID, temperature=20, gravity=1)
            session.add(planet)

            # Ensure Item exists
            res = await session.execute(select(Item).where(Item.name == TEST_ITEM_NAME))
            item = res.scalars().first()
            if not item:
                item = Item(name=TEST_ITEM_NAME, tier=1, volume=1.0)
                session.add(item)
                await session.commit() # commit item to get ID
                await session.refresh(item)

            item_id = item.id
            inventory = Inventory(planet_id=TEST_PLANET_ID, item_id=item_id, quantity=100)
            session.add(inventory)

            await session.commit()

        # EXECUTE
        payload = {"type": "IRON_MINE"}
        response = await ac.post(f"/api/v1/planets/{TEST_PLANET_ID}/build", json=payload)

        # VERIFY
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["type"] == "IRON_MINE"
        assert data["status"] == "constructing"
        assert data["planet_id"] == TEST_PLANET_ID

        # CHECK DB SIDE EFFECTS
        async with SessionLocal() as session:
            # Check Balance
            res = await session.execute(select(Balance).where(Balance.user_id == TEST_USER_ID, Balance.currency_type == "CRED"))
            balance = res.scalars().first()
            # 500 - 100 = 400
            assert balance.amount == Decimal(400)

            # Check Inventory
            # Iron Mine costs 10 Iron. 100 - 10 = 90
            res = await session.execute(select(Inventory).where(Inventory.planet_id == TEST_PLANET_ID, Inventory.item_id == item_id))
            inv = res.scalars().first()
            assert inv.quantity == 90

@pytest.mark.asyncio
async def test_build_insufficient_funds():
     async with AsyncClient(app=app, base_url="http://test") as ac:
        # Assuming previous test setup, but let's just modify wallet
        async with SessionLocal() as session:
            res = await session.execute(select(Balance).where(Balance.user_id == TEST_USER_ID, Balance.currency_type == "CRED"))
            balance = res.scalars().first()
            balance.amount = 0 # bankrupt
            await session.commit()

        payload = {"type": "IRON_MINE"}
        response = await ac.post(f"/api/v1/planets/{TEST_PLANET_ID}/build", json=payload)

        assert response.status_code == 400
        assert "Insufficient credits" in response.text

@pytest.mark.asyncio
async def test_get_buildings():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/planets/{TEST_PLANET_ID}/buildings")
        assert response.status_code == 200
        data = response.json()
        # Should have at least the one from previous test (unless I bankrupt it first? Tests order matters)
        # Pytest async execution order is usually by definition order.
        # But `test_build_structure` ran first.
        # `test_build_insufficient_funds` ran second.
        # So there should be 1 building.
        assert isinstance(data, list)
