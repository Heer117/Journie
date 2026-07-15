import httpx
import random
import string
import sys

BASE_URL = "http://127.0.0.1:8000"

def get_random_string(length=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def run_tests():
    email = f"test_{get_random_string()}@example.com"
    password = "password123"
    name = "Test User"

    print("--- Starting Deletion and Status API Tests ---")
    
    # 1. Sign up a new user
    print(f"1. Signing up user with email: {email}")
    signup_res = httpx.post(f"{BASE_URL}/auth/signup", json={
        "name": name,
        "email": email,
        "password": password
    })
    
    if signup_res.status_code != 200:
        print(f"FAIL: Signup failed with status {signup_res.status_code}: {signup_res.text}")
        sys.exit(1)
        
    signup_data = signup_res.json()
    token = signup_data["access_token"]
    user_id = signup_data["user_id"]
    print(f"SUCCESS: Signed up user ID {user_id}")
    
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get hotels to use for booking
    hotels_res = httpx.get(f"{BASE_URL}/bookings/hotels", headers=headers)
    hotels = hotels_res.json()
    target_hotel = hotels[0]

    # 3. Create a booking
    print("\n2. Creating a booking...")
    booking_data = {
        "hotel_id": target_hotel["id"],
        "destination": target_hotel["destination"],
        "start_date": "2026-08-01",
        "end_date": "2026-08-10",
        "passport_expiry": "2028-12-31"
    }
    booking_res = httpx.post(f"{BASE_URL}/bookings/", headers=headers, json=booking_data)
    assert booking_res.status_code == 200, f"Booking creation failed: {booking_res.text}"
    booking = booking_res.json()
    booking_id = booking["id"]
    print(f"SUCCESS: Created booking with ID {booking_id}, status: {booking.get('status')}")
    assert booking.get("status") == "active"

    # 4. Fetch list (default status=active)
    print("3. Fetching bookings (default status=active)...")
    get_res = httpx.get(f"{BASE_URL}/bookings/", headers=headers)
    assert get_res.status_code == 200
    active_bookings = get_res.json()
    assert any(b["id"] == booking_id for b in active_bookings)
    print("SUCCESS: Booking listed in active bookings.")

    # 5. Delete (cancel) the booking
    print(f"4. Cancelling booking {booking_id}...")
    del_res = httpx.delete(f"{BASE_URL}/bookings/{booking_id}", headers=headers)
    assert del_res.status_code == 200, f"Cancellation failed: {del_res.text}"
    print("SUCCESS: Cancellation request succeeded.")

    # 6. Fetch list again (default status=active) - should be empty/missing
    print("5. Verifying booking is not in active bookings...")
    get_active_res = httpx.get(f"{BASE_URL}/bookings/?status=active", headers=headers)
    assert get_active_res.status_code == 200
    active_bookings_after = get_active_res.json()
    assert not any(b["id"] == booking_id for b in active_bookings_after)
    print("SUCCESS: Booking is hidden from active list.")

    # 7. Fetch cancelled bookings
    print("6. Fetching cancelled bookings...")
    get_cancelled_res = httpx.get(f"{BASE_URL}/bookings/?status=cancelled", headers=headers)
    assert get_cancelled_res.status_code == 200
    cancelled_bookings = get_cancelled_res.json()
    assert any(b["id"] == booking_id for b in cancelled_bookings)
    print("SUCCESS: Booking is found in cancelled list.")

    # 8. Fetch all bookings
    print("7. Fetching all bookings (status=all)...")
    get_all_res = httpx.get(f"{BASE_URL}/bookings/?status=all", headers=headers)
    assert get_all_res.status_code == 200
    all_bookings = get_all_res.json()
    assert any(b["id"] == booking_id for b in all_bookings)
    print("SUCCESS: Booking is found in all bookings list.")

    # 9. Create a group trip consensus plan
    print("\n8. Creating a group trip consensus plan...")
    trip_payload = {
        "trip_name": "Test Group Trip",
        "destination": "Paris",
        "num_nights": 3,
        "members": [
            {"name": "Alice", "budget": 1000.0, "preferences": ["wifi"]},
            {"name": "Bob", "budget": 500.0, "preferences": ["wifi"]}
        ]
    }
    trip_res = httpx.post(f"{BASE_URL}/group-trips/", headers=headers, json=trip_payload)
    assert trip_res.status_code == 201, f"Trip creation failed: {trip_res.text}"
    trip = trip_res.json()
    trip_id = trip["id"]
    print(f"SUCCESS: Created group trip plan with ID {trip_id}, status: {trip.get('status')}")
    assert trip.get("status") == "active"

    # 10. Fetch list (default status=active)
    print("9. Fetching group trips (default status=active)...")
    get_trips_res = httpx.get(f"{BASE_URL}/group-trips/", headers=headers)
    assert get_trips_res.status_code == 200
    active_trips = get_trips_res.json()
    assert any(t["id"] == trip_id for t in active_trips)
    print("SUCCESS: Group trip listed in active trips.")

    # 11. Delete (cancel) the group trip plan
    print(f"10. Cancelling group trip {trip_id}...")
    del_trip_res = httpx.delete(f"{BASE_URL}/group-trips/{trip_id}", headers=headers)
    assert del_trip_res.status_code == 200, f"Trip cancellation failed: {del_trip_res.text}"
    print("SUCCESS: Group trip cancellation request succeeded.")

    # 12. Verify not in active trips
    print("11. Verifying group trip is not in active trips...")
    get_active_trips = httpx.get(f"{BASE_URL}/group-trips/?status=active", headers=headers)
    assert get_active_trips.status_code == 200
    active_trips_after = get_active_trips.json()
    assert not any(t["id"] == trip_id for t in active_trips_after)
    print("SUCCESS: Group trip is hidden from active list.")

    # 13. Verify in cancelled trips
    print("12. Fetching cancelled group trips...")
    get_cancelled_trips = httpx.get(f"{BASE_URL}/group-trips/?status=cancelled", headers=headers)
    assert get_cancelled_trips.status_code == 200
    cancelled_trips = get_cancelled_trips.json()
    assert any(t["id"] == trip_id for t in cancelled_trips)
    print("SUCCESS: Group trip is found in cancelled list.")

    # 14. Verify in all trips
    print("13. Fetching all group trips (status=all)...")
    get_all_trips = httpx.get(f"{BASE_URL}/group-trips/?status=all", headers=headers)
    assert get_all_trips.status_code == 200
    all_trips = get_all_trips.json()
    assert any(t["id"] == trip_id for t in all_trips)
    print("SUCCESS: Group trip is found in all trips list.")

    print("\n--- ALL DELETION AND STATUS API TESTS PASSED SUCCESSFULLY! ---")

if __name__ == "__main__":
    run_tests()
