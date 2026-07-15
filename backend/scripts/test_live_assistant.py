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

    print("--- Starting Live Assistant Feature Tests ---")
    
    # 1. Sign up a new user
    print(f"1. Signing up user: {email}")
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
    print(f"SUCCESS: User signed up with ID {user_id}")
    
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get list of hotels and create booking
    print("2. Fetching available hotels to create booking...")
    hotels_res = httpx.get(f"{BASE_URL}/bookings/hotels", headers=headers)
    if hotels_res.status_code != 200:
        print(f"FAIL: Fetching hotels failed: {hotels_res.text}")
        sys.exit(1)
        
    hotels = hotels_res.json()
    if not hotels:
        print("FAIL: No hotels found in database. Seed mock hotels first.")
        sys.exit(1)
        
    target_hotel = hotels[0]
    hotel_name = target_hotel["name"]
    destination = target_hotel["destination"]
    print(f"Selected Hotel: {hotel_name} in {destination}")

    # Create the booking
    booking_data = {
        "hotel_id": target_hotel["id"],
        "destination": destination,
        "start_date": "2026-09-01",
        "end_date": "2026-09-07",
        "passport_expiry": "2029-01-01"
    }
    
    booking_res = httpx.post(f"{BASE_URL}/bookings/", headers=headers, json=booking_data)
    if booking_res.status_code != 200:
        print(f"FAIL: Creating booking failed: {booking_res.text}")
        sys.exit(1)
        
    booking = booking_res.json()
    booking_id = booking["id"]
    print(f"SUCCESS: Created booking ID: {booking_id}")

    # 3. Call /chat/ with booking_id context
    print("3. Sending chat request with booking context...")
    chat_payload = {
        "message": f"Where am I staying and what is my destination? Reply in one brief sentence mentioning both '{hotel_name}' and '{destination}'.",
        "booking_id": booking_id
    }
    
    chat_res = httpx.post(f"{BASE_URL}/chat/", headers=headers, json=chat_payload)
    if chat_res.status_code != 200:
        print(f"FAIL: Chat request failed with status {chat_res.status_code}: {chat_res.text}")
        sys.exit(1)
        
    chat_data = chat_res.json()
    reply = chat_data["reply"]
    print(f"SUCCESS: Assistant replied: \"{reply}\"")
    
    # Assertions on response
    assert hotel_name.lower() in reply.lower(), f"Expected hotel name '{hotel_name}' in reply"
    assert destination.lower() in reply.lower(), f"Expected destination '{destination}' in reply"
    
    # Check for no emojis
    emoji_chars = [c for c in reply if ord(c) > 0x1F000 or (0x2000 <= ord(c) <= 0x32FF)]
    assert not emoji_chars, f"Emojis detected in assistant reply: {emoji_chars}"
    print("SUCCESS: Checked that response contains no emojis.")

    # 4. Error handling tests
    # Invalid ObjectId format should return 400
    print("4. Testing invalid booking ID format...")
    invalid_chat_payload = {
        "message": "Hello",
        "booking_id": "not-an-object-id"
    }
    invalid_res = httpx.post(f"{BASE_URL}/chat/", headers=headers, json=invalid_chat_payload)
    print(f"Status for invalid ID format: {invalid_res.status_code} (Expected: 400)")
    assert invalid_res.status_code == 400
    assert "Invalid booking ID format" in invalid_res.json()["detail"]

    # Non-existent booking ID (valid format but not in DB) should return 404
    print("5. Testing non-existent booking ID...")
    nonexistent_booking_id = "60a8e46e50970d461f384407" # valid objectid format
    nonexistent_payload = {
        "message": "Hello",
        "booking_id": nonexistent_booking_id
    }
    nonexistent_res = httpx.post(f"{BASE_URL}/chat/", headers=headers, json=nonexistent_payload)
    print(f"Status for non-existent booking: {nonexistent_res.status_code} (Expected: 404)")
    assert nonexistent_res.status_code == 404
    assert "Booking not found" in nonexistent_res.json()["detail"]

    print("\n--- ALL LIVE ASSISTANT TESTS PASSED SUCCESSFULLY! ---")

if __name__ == "__main__":
    run_tests()
