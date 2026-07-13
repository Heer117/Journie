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

    print("--- Starting Booking Flow API Tests ---")
    
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
    print("2. Fetching all available hotels...")
    hotels_res = httpx.get(f"{BASE_URL}/bookings/hotels", headers=headers)
    if hotels_res.status_code != 200:
        print(f"FAIL: Fetching hotels failed: {hotels_res.text}")
        sys.exit(1)
        
    hotels = hotels_res.json()
    print(f"SUCCESS: Found {len(hotels)} hotels")
    if not hotels:
        print("FAIL: No hotels found in database. Did you seed?")
        sys.exit(1)
        
    # Pick the first hotel
    target_hotel = hotels[0]
    print(f"Selected Hotel: {target_hotel['name']} in {target_hotel['destination']}")

    # 3. Create a booking
    print("3. Creating a new booking...")
    booking_data = {
        "hotel_id": target_hotel["id"],
        "destination": target_hotel["destination"],
        "start_date": "2026-08-01",
        "end_date": "2026-08-10",
        "passport_expiry": "2028-12-31"
      }
    
    booking_res = httpx.post(f"{BASE_URL}/bookings/", headers=headers, json=booking_data)
    if booking_res.status_code != 200:
        print(f"FAIL: Creating booking failed with status {booking_res.status_code}: {booking_res.text}")
        sys.exit(1)
        
    created_booking = booking_res.json()
    print(f"SUCCESS: Booking created with ID {created_booking['id']}")
    assert created_booking["hotel_name"] == target_hotel["name"]
    assert created_booking["destination"] == target_hotel["destination"]
    
    # 4. Fetch list of bookings
    print("4. Fetching user bookings...")
    list_res = httpx.get(f"{BASE_URL}/bookings/", headers=headers)
    if list_res.status_code != 200:
        print(f"FAIL: Fetching user bookings failed: {list_res.text}")
        sys.exit(1)
        
    bookings_list = list_res.json()
    print(f"SUCCESS: Found {len(bookings_list)} bookings for the user")
    assert len(bookings_list) >= 1
    assert bookings_list[0]["id"] == created_booking["id"]
    
    print("\n--- ALL API TESTS PASSED SUCCESSFULLY! ---")

if __name__ == "__main__":
    run_tests()
