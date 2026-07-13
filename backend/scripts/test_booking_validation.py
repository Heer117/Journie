import httpx
import random
import string
import sys
import datetime

BASE_URL = "http://127.0.0.1:8000"

def get_random_string(length=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def run_validation_tests():
    email = f"test_{get_random_string()}@example.com"
    password = "password123"
    name = "Test User"

    print("--- Starting Booking Validation API Tests ---")
    
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

    # Helper function to try booking and assert status code
    def attempt_booking(data, expected_status_code=400, expected_msg=None):
        res = httpx.post(f"{BASE_URL}/bookings/", headers=headers, json=data)
        print(f"   Response status: {res.status_code}, response: {res.text}")
        
        if res.status_code != expected_status_code:
            print(f"   FAIL: Expected status {expected_status_code}, got {res.status_code}")
            return False
            
        if expected_msg:
            # Check either field validator message or 400 Bad Request error detail
            response_text = res.text
            if expected_msg not in response_text:
                print(f"   FAIL: Expected message '{expected_msg}' not found in response text")
                return False
                
        print("   PASS")
        return True

    # 3. Test Cases
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    tomorrow_str = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    yesterday_str = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    far_future_str = (datetime.date.today() + datetime.timedelta(days=1000)).strftime("%Y-%m-%d")

    # A. Valid Booking (Sanity Check)
    print("\nCase A: Attempting a VALID booking (start_date=tomorrow, end_date=tomorrow+5, passport=future)...")
    valid_data = {
        "hotel_id": target_hotel["id"],
        "destination": target_hotel["destination"],
        "start_date": tomorrow_str,
        "end_date": (datetime.date.today() + datetime.timedelta(days=5)).strftime("%Y-%m-%d"),
        "passport_expiry": far_future_str
    }
    success = attempt_booking(valid_data, expected_status_code=200)
    if not success:
        sys.exit(1)

    # B. Past Check-in Date
    print("\nCase B: Attempting booking with check-in date in the PAST...")
    past_checkin_data = valid_data.copy()
    past_checkin_data["start_date"] = yesterday_str
    success = attempt_booking(past_checkin_data, expected_status_code=400, expected_msg="Check-in date cannot be in the past.")
    if not success:
        # Check if 422 was returned instead (Pydantic validator)
        success = attempt_booking(past_checkin_data, expected_status_code=422, expected_msg="Check-in date cannot be in the past.")
        if not success:
            sys.exit(1)

    # C. Check-out date before Check-in date
    print("\nCase C: Attempting booking with check-out date BEFORE check-in date...")
    invalid_range_data = valid_data.copy()
    invalid_range_data["start_date"] = tomorrow_str
    invalid_range_data["end_date"] = yesterday_str
    success = attempt_booking(invalid_range_data, expected_status_code=400, expected_msg="Check-out date must be strictly after check-in date.")
    if not success:
        success = attempt_booking(invalid_range_data, expected_status_code=422, expected_msg="Check-out date must be strictly after check-in date.")
        if not success:
            sys.exit(1)

    # D. Check-out date equal to Check-in date
    print("\nCase D: Attempting booking with check-out date EQUAL to check-in date...")
    same_date_data = valid_data.copy()
    same_date_data["start_date"] = tomorrow_str
    same_date_data["end_date"] = tomorrow_str
    success = attempt_booking(same_date_data, expected_status_code=400, expected_msg="Check-out date must be strictly after check-in date.")
    if not success:
        success = attempt_booking(same_date_data, expected_status_code=422, expected_msg="Check-out date must be strictly after check-in date.")
        if not success:
            sys.exit(1)

    # E. Expired Passport
    print("\nCase E: Attempting booking with an already EXPIRED passport...")
    expired_passport_data = valid_data.copy()
    expired_passport_data["passport_expiry"] = yesterday_str
    success = attempt_booking(expired_passport_data, expected_status_code=400, expected_msg="Passport expiry date must be in the future.")
    if not success:
        success = attempt_booking(expired_passport_data, expected_status_code=422, expected_msg="Passport expiry date must be in the future.")
        if not success:
            sys.exit(1)

    print("\n--- ALL BOOKING VALIDATION API TESTS PASSED SUCCESSFULLY! ---")

if __name__ == "__main__":
    run_validation_tests()
