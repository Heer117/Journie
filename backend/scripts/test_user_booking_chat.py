import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.utils.security import create_access_token
from app.db import users_collection, bookings_collection

async def main():
    print("--- Testing /chat/ with user bookings ---")
    
    test_user = await users_collection.find_one({"email": "test_agent_with_booking@example.com"})
    if not test_user:
        res = await users_collection.insert_one({
            "name": "Booking User",
            "email": "test_agent_with_booking@example.com",
            "password_hash": "hash"
        })
        user_id = str(res.inserted_id)
    else:
        user_id = str(test_user["_id"])

    # Ensure a booking exists for this user
    booking = await bookings_collection.find_one({"user_id": user_id})
    if not booking:
        await bookings_collection.insert_one({
            "user_id": user_id,
            "hotel_id": "hotel_123",
            "hotel_name": "Taj Lake Palace",
            "destination": "Udaipur",
            "start_date": "2026-07-22",
            "end_date": "2026-07-25",
            "passport_expiry": "2029-01-01",
            "status": "active",
            "document_check": {"status": "Ready"}
        })

    token = create_access_token(user_id)
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        print("Sending chat request: 'Can you check my current bookings and tell me the details of my upcoming trips?'")
        res = await client.post("/chat/", json={"message": "Can you check my current bookings and tell me the details of my upcoming trips?"}, headers=headers)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.text}")

if __name__ == "__main__":
    asyncio.run(main())
