import httpx
import random
import string
import sys
import datetime

BASE_URL = "http://127.0.0.1:8000"

def get_random_string(length=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def run_tests():
    email = f"test_{get_random_string()}@example.com"
    password = "password123"
    name = "Test User"

    print("--- Starting Date Overlap and On-Behalf-Of API Tests ---")
    
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

    # 2. Get list of hotels
    print("2. Fetching available hotels...")
    hotels_res = httpx.get(f"{BASE_URL}/bookings/hotels", headers=headers)
    if hotels_res.status_code != 200:
        print(f"FAIL: Fetching hotels failed: {hotels_res.text}")
        sys.exit(1)
        
    hotels = hotels_res.json()
    if not hotels:
        print("FAIL: No hotels found in database. Did you seed?")
        sys.exit(1)
        
    target_hotel = hotels[0]
    print(f"Selected Hotel: {target_hotel['name']} in {target_hotel['destination']}")

    # 3. Create a primary booking (July 20 to July 25, 2026)
    print("\n3. Creating first booking (July 20 to July 25)...")
    booking_1_data = {
        "hotel_id": target_hotel["id"],
        "destination": target_hotel["destination"],
        "start_date": "2026-07-20",
        "end_date": "2026-07-25",
        "passport_expiry": "2030-01-01"
    }
    res_1 = httpx.post(f"{BASE_URL}/bookings/", headers=headers, json=booking_1_data)
    if res_1.status_code != 200:
        print(f"FAIL: First booking failed: {res_1.text}")
        sys.exit(1)
    
    created_booking_1 = res_1.json()
    print(f"SUCCESS: Created booking ID {created_booking_1['id']}")

    # 4. Attempt to book an overlapping trip (July 22 to July 24, 2026) for self
    print("\n4. Attempting overlapping booking (July 22 to July 24) for self...")
    booking_2_data = {
        "hotel_id": target_hotel["id"],
        "destination": target_hotel["destination"],
        "start_date": "2026-07-22",
        "end_date": "2026-07-24",
        "passport_expiry": "2030-01-01"
    }
    res_2 = httpx.post(f"{BASE_URL}/bookings/", headers=headers, json=booking_2_data)
    print(f"Response status: {res_2.status_code}, detail: {res_2.text}")
    
    if res_2.status_code != 400:
        print(f"FAIL: Expected 400 Bad Request, got {res_2.status_code}")
        sys.exit(1)
        
    res_2_data = res_2.json()
    expected_warning = "You already have a booking from 2026-07-20 to 2026-07-25 that overlaps these dates."
    if res_2_data.get("detail") != expected_warning:
        print(f"FAIL: Expected warning '{expected_warning}', got '{res_2_data.get('detail')}'")
        sys.exit(1)
    print("PASS: Silently blocked with expected overlap message.")

    # 5. Re-attempt booking with booked_for object (on behalf of guest)
    print("\n5. Re-attempting overlapping booking on behalf of guest...")
    booking_3_data = booking_2_data.copy()
    booking_3_data["booked_for"] = {
        "name": "Jane Doe",
        "phone": "+1 555-0199",
        "relation": "Sister"
    }
    
    res_3 = httpx.post(f"{BASE_URL}/bookings/", headers=headers, json=booking_3_data)
    if res_3.status_code != 200:
        print(f"FAIL: Bypassing overlap validation failed: {res_3.text}")
        sys.exit(1)
        
    created_booking_3 = res_3.json()
    print(f"SUCCESS: Bypassed warning and created booking ID {created_booking_3['id']}")
    
    # 6. Verify retrieved booking contains booked_for details
    print("\n6. Verifying booked_for details on retrieved bookings...")
    list_res = httpx.get(f"{BASE_URL}/bookings/", headers=headers)
    if list_res.status_code != 200:
        print(f"FAIL: Fetching bookings list failed: {list_res.text}")
        sys.exit(1)
        
    bookings_list = list_res.json()
    # Find the newly created guest booking
    guest_booking = next((b for b in bookings_list if b["id"] == created_booking_3["id"]), None)
    
    if not guest_booking:
        print("FAIL: Guest booking not found in active list")
        sys.exit(1)
        
    booked_for = guest_booking.get("booked_for")
    if not booked_for:
        print("FAIL: booked_for field is missing from retrieve response")
        sys.exit(1)
        
    assert booked_for["name"] == "Jane Doe"
    assert booked_for["phone"] == "+1 555-0199"
    assert booked_for["relation"] == "Sister"
    print("PASS: Retrieved guest booking matches all guest fields.")

    print("\n--- ALL DATE OVERLAP AND ON-BEHALF-OF API TESTS PASSED SUCCESSFULLY! ---")
