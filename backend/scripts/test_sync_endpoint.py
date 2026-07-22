import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.utils.security import create_access_token
from app.db import users_collection, bookings_collection

async def main():
    print("=== Testing /chat/ booking_updated sync response ===")
    
    # Use/create a test user
    email = "sync_test_user@example.com"
    test_user = await users_collection.find_one({"email": email})
    if not test_user:
        res = await users_collection.insert_one({
            "name": "Sync Test User",
            "email": email,
            "password_hash": "hash"
        })
        user_id = str(res.inserted_id)
    else:
        user_id = str(test_user["_id"])

    # Clear bookings for clean run
    await bookings_collection.delete_many({"user_id": user_id})
    
    token = create_access_token(user_id)
    headers = {"Authorization": f"Bearer {token}"}
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Step 1: Start booking Taj Exotica Resort & Spa
        print("\nSending Message 1: I want to book Taj Exotica Resort & Spa, Goa from 2026-11-10 to 2026-11-15.")
        res1 = await client.post("/chat/", json={"message": "I want to book Taj Exotica Resort & Spa, Goa from 2026-11-10 to 2026-11-15."}, headers=headers)
        print(f"Response 1 Status: {res1.status_code}")
        print(f"Response 1 Body: {res1.json()}")
        
        # Step 2: Confirm booking to trigger tool execution
        print("\nSending Message 2: Yes, please proceed.")
        res2 = await client.post("/chat/", json={"message": "Yes, please proceed."}, headers=headers)
        print(f"Response 2 Status: {res2.status_code}")
        print(f"Response 2 Body: {res2.json()}")

if __name__ == "__main__":
    asyncio.run(main())
