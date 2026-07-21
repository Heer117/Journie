import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.utils.security import create_access_token
from app.db import users_collection

async def main():
    print("--- Direct ASGI Test for /chat/ Endpoint ---")
    
    # Create or fetch a test user
    test_user = await users_collection.find_one({"email": "test_agent_debug@example.com"})
    if not test_user:
        res = await users_collection.insert_one({
            "name": "Debug User",
            "email": "test_agent_debug@example.com",
            "password_hash": "hash"
        })
        user_id = str(res.inserted_id)
    else:
        user_id = str(test_user["_id"])

    token = create_access_token(user_id)
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        print("Sending chat request 1: Weather in Udaipur...")
        res1 = await client.post("/chat/", json={"message": "What is the weather forecast for Udaipur on 2026-07-23?"}, headers=headers)
        print(f"Status 1: {res1.status_code}")
        print(f"Response 1: {res1.text}")

        print("\nSending chat request 2: User bookings...")
        res2 = await client.post("/chat/", json={"message": "Can you check my current bookings?"}, headers=headers)
        print(f"Status 2: {res2.status_code}")
        print(f"Response 2: {res2.text}")

if __name__ == "__main__":
    asyncio.run(main())
