import asyncio
import os
import sys
import httpx

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

async def test_suggestions_api():
    print("--- Testing Phase E AI Suggestions Endpoint (In-Memory ASGI) ---")
    
    # 1. Fetch suggestions without authentication (should be blocked)
    print("\n1. Testing Unauthenticated Request...")
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app)) as client:
        res = await client.get("http://localhost:8000/bookings/suggestions?destination=Paris&start_date=2026-09-12&end_date=2026-09-15")
    
    print(f"Status Code: {res.status_code}")
    assert res.status_code in [401, 422], "Expected 401 or 422 for missing auth header"
    print("-> Unauthenticated Request Blocked Successfully!")

    # 2. Authenticated Request
    print("\n2. Testing Authenticated Request...")
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), timeout=30.0) as client:
        # Try login first
        login_res = await client.post("http://localhost:8000/auth/login", json={"email": "test_suggestions@example.com", "password": "password123"})
        if login_res.status_code != 200:
            # Try signup if not exists
            print(f"Test user login failed ({login_res.status_code}). Attempting signup...")
            signup_res = await client.post("http://localhost:8000/auth/signup", json={"email": "test_suggestions@example.com", "password": "password123", "name": "Test Traveler"})
            print(f"Signup Status: {signup_res.status_code}, Body: {signup_res.text}")
            login_res = await client.post("http://localhost:8000/auth/login", json={"email": "test_suggestions@example.com", "password": "password123"})
        
        assert login_res.status_code == 200, f"Login failed with code {login_res.status_code}: {login_res.text}"
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print("Fetching travel suggestions...")
        res_auth = await client.get(
            "http://localhost:8000/bookings/suggestions?destination=Paris&start_date=2026-09-12&end_date=2026-09-15",
            headers=headers
        )
        
    print(f"Status Code: {res_auth.status_code}")
    assert res_auth.status_code == 200, f"Expected 200 OK, got {res_auth.status_code}"
    payload = res_auth.json()
    assert "suggestions" in payload, "Missing 'suggestions' key in response"
    print(f"Suggestions Output:\n{payload['suggestions']}")
    assert "Paris" in payload["suggestions"] or "Highlights" in payload["suggestions"] or "Seasonal" in payload["suggestions"], "Unexpected suggestions payload contents"
    print("-> Authenticated Request Succeeded and returned valid suggestions!")
    
    print("\n=== ALL SUGGESTIONS API TESTS PASSED PERFECTLY! ===")

if __name__ == "__main__":
    asyncio.run(test_suggestions_api())
