import pytest
import pytest_asyncio
from httpx import AsyncClient
from app.main import app
from app.api import deps
from app.db.session import SessionLocal
from app.models.user import User
from app.models.wallet import Balance
from app.models.planet import Planet
from app.models.item import Item
from app.models.inventory import Inventory
from app.models.fleet import Fleet
from sqlalchemy import select
from app.services.galaxy import initialize_galaxy
import random
from decimal import Decimal

API_PREFIX = "/api/v1"

# Mock Users
async def get_test_issuer():
    async with SessionLocal() as session:
        user = await session.execute(select(User).where(User.username == "issuer"))
        return user.scalar_one()

async def get_test_contractor():
    async with SessionLocal() as session:
        user = await session.execute(select(User).where(User.username == "contractor"))
        return user.scalar_one()

@pytest_asyncio.fixture(scope="function")
async def setup_db():
    from app.db.session import engine
    from app.models.base import Base
    # Import all models so Base knows about them
    from app.models import user, planet, item, inventory, wallet, building, fleet, contract

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_contract_flow(setup_db):
    # Setup Data
    async with SessionLocal() as session:
        await initialize_galaxy(session, planet_count=10)

        # Create Unique Users
        suffix = random.randint(1000, 9999)
        issuer_id_val = random.randint(100000000000000000, 900000000000000000)
        contractor_id_val = random.randint(100000000000000000, 900000000000000000)

        issuer = User(id=issuer_id_val, username="issuer")
        contractor = User(id=contractor_id_val, username="contractor")
        session.add_all([issuer, contractor])
        await session.commit()
        await session.refresh(issuer)
        await session.refresh(contractor)

        # Store IDs before further commits expire them
        issuer_id = issuer.id
        contractor_id = contractor.id

        # Create Balances
        # Issuer has 10000 CRED
        b1 = Balance(user_id=issuer_id, currency_type="CRED", amount=Decimal(10000.0))
        # Contractor has 5000 CRED
        b2 = Balance(user_id=contractor_id, currency_type="CRED", amount=Decimal(5000.0))
        session.add_all([b1, b2])

        # Create Item
        item = Item(name=f"Test Cargo {suffix}", tier=1, volume=1.0)
        session.add(item)
        await session.commit()
        await session.refresh(item)
        item_id = item.id

        # Get Planets
        planets_res = await session.execute(select(Planet).limit(2))
        planets = planets_res.scalars().all()
        origin = planets[0]
        destination = planets[1]
        origin_id = origin.id
        dest_id = destination.id

        # Create Inventory for Issuer at Origin
        inv = Inventory(planet_id=origin_id, item_id=item_id, quantity=100)
        session.add(inv)

        # Create Fleet for Contractor at Origin
        fleet = Fleet(owner_id=contractor_id, name="Hauler 1", location_planet_id=origin_id, cargo_capacity=500.0)
        session.add(fleet)

        await session.commit()
        await session.refresh(fleet)
        fleet_id = fleet.id

    # Test Client
    async with AsyncClient(app=app, base_url="http://test") as ac:

        # 1. Create Contract (as Issuer)
        app.dependency_overrides[deps.get_current_user] = get_test_issuer

        contract_data = {
            "origin_planet_id": origin_id,
            "destination_planet_id": dest_id,
            "item_id": item_id,
            "quantity": 50,
            "currency_type": "CRED", # Explicitly set currency type
            "reward_amount": 1000.0,
            "collateral_amount": 2000.0,
            "duration_seconds": 3600
        }

        res = await ac.post(f"{API_PREFIX}/contracts/", json=contract_data)
        assert res.status_code == 200, res.text
        contract = res.json()
        contract_id = contract["id"]
        assert contract["status"] == "OPEN"

        # 2. Accept Contract (as Contractor)
        app.dependency_overrides[deps.get_current_user] = get_test_contractor

        res = await ac.post(f"{API_PREFIX}/contracts/{contract_id}/accept", params={"fleet_id": fleet_id})
        assert res.status_code == 200, res.text
        contract = res.json()
        assert contract["status"] == "IN_PROGRESS"

        # 3. Move Fleet (as Contractor)
        # Move to destination
        move_data = {
            "destination_planet_id": dest_id
        }
        res = await ac.post(f"{API_PREFIX}/fleets/{fleet_id}/move", json=move_data)
        assert res.status_code == 200

        # Force Arrive (Hack: Modify DB directly)
        async with SessionLocal() as session:
            f = await session.get(Fleet, fleet_id)
            from datetime import datetime, timezone
            # Set arrival time to 1 second ago
            f.arrival_time = datetime.now(timezone.utc)
            await session.commit()

        # Call arrive endpoint
        res = await ac.post(f"{API_PREFIX}/fleets/{fleet_id}/arrive")
        assert res.status_code == 200

        # 4. Complete Contract (as Contractor)
        res = await ac.post(f"{API_PREFIX}/contracts/{contract_id}/complete", params={"fleet_id": fleet_id})
        assert res.status_code == 200, res.text
        contract = res.json()
        assert contract["status"] == "COMPLETED"

    # Verify Final State
    async with SessionLocal() as session:
        # Check Issuer Inventory at Dest
        inv = await session.scalar(select(Inventory).where(Inventory.planet_id == dest_id, Inventory.item_id == item_id))
        assert inv is not None
        assert inv.quantity >= 50

        # Check Contractor Balance (Initial 5000 - 2000 Collat + 1000 Reward + 2000 Collat Return = 6000)
        b = await session.scalar(select(Balance).where(Balance.user_id == contractor_id, Balance.currency_type == "CRED"))
        assert b.amount == Decimal(6000.0)

    # Cleanup overrides
    app.dependency_overrides = {}
