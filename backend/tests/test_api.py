import pytest
from httpx import AsyncClient
from app.main import app
from app.db.session import SessionLocal
from app.services.galaxy import initialize_galaxy

# API prefix
API_PREFIX = "/api/v1"

@pytest.mark.asyncio
async def test_create_item_and_inventory():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Initialize Galaxy if needed (manually triggering since AsyncClient might not run lifespan automatically in this setup)
        # Note: In a proper test setup, we would use a fixture or LifespanManager.
        async with SessionLocal() as session:
             await initialize_galaxy(session, planet_count=5)

        # 0. Login
        login_data = {"username": "testuser"}
        response = await ac.post(f"{API_PREFIX}/auth/dev-login", json=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Create Item
        import random
        random_suffix = random.randint(1000, 9999)
        item_name = f"Test Iron Ore {random_suffix}"

        item_data = {
            "name": item_name,
            "description": "Raw iron ore for testing",
            "tier": 1,
            "volume": 1.0
        }
        response = await ac.post(f"{API_PREFIX}/items/", json=item_data, headers=headers)

        if response.status_code == 200:
            item_id = response.json()["id"]
        else:
            # Fallback (should ideally not happen with random suffix unless collision)
            response = await ac.get(f"{API_PREFIX}/items/", headers=headers)
            items = response.json()
            found_item = next((i for i in items if i["name"] == item_name), None)
            if found_item:
                 item_id = found_item["id"]
            else:
                 # If creation failed but not found, maybe re-raise or fail
                 assert response.status_code == 200

        # 2. Get Planets
        response = await ac.get(f"{API_PREFIX}/planets/", headers=headers)
        planets = response.json()
        assert len(planets) > 0
        planet_id = planets[0]["id"]

        # 3. Add Inventory
        inventory_data = {
            "item_id": item_id,
            "quantity": 100
        }
        response = await ac.post(f"{API_PREFIX}/planets/{planet_id}/inventory", json=inventory_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["planet_id"] == planet_id
        assert data["item_id"] == item_id
        assert data["quantity"] >= 100

        # 4. Get Inventory
        response = await ac.get(f"{API_PREFIX}/planets/{planet_id}/inventory", headers=headers)
        assert response.status_code == 200
        inventory_list = response.json()
        assert len(inventory_list) > 0
        found = any(i["item_id"] == item_id for i in inventory_list)
        assert found
