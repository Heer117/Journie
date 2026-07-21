import asyncio
import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.llm_service import run_agent_chat
from app.db import users_collection, bookings_collection

async def test_phase_d():
    print("--- Testing Phase D Agentic Booking & Cancellation Tools ---")
    
    # 1. Fetch or create a test user
    user = await users_collection.find_one({"email": "test@example.com"})
    if not user:
        user_res = await users_collection.insert_one({"email": "test@example.com", "full_name": "Test Traveler"})
        user_id = str(user_res.inserted_id)
    else:
        user_id = str(user["_id"])
        
    print(f"Using Test User ID: {user_id}")
    await bookings_collection.delete_many({"user_id": user_id})
    
    system_prompt = (
        "You are Journie, a helpful, grounded AI travel assistant. "
        "You have access to tools for checking user bookings (`get_user_trips`), checking weather forecasts (`get_weather`), "
        "searching tourist sights (`search_places`), searching available hotels (`search_hotels`), creating bookings (`create_booking`), "
        "and cancelling bookings (`cancel_booking`).\n\n"
        "NEVER use any emojis in your response."
    )
    
    # Test 1: Search Hotels
    print("\n1. Testing Hotel Search via Chat...")
    reply_1 = await run_agent_chat(
        system_prompt=system_prompt,
        user_message="What hotels do you have available in Goa?",
        chat_history=[],
        user_id=user_id
    )
    print(f"Assistant Reply:\n{reply_1}")
    assert any(k in reply_1.lower() for k in ["goa", "hotel", "resort", "hyatt", "book", "available"]), "Hotel search failed"
    print("-> Hotel Search Test Passed!")
    
    # Test 2: Create Booking via Agent (Conversational Confirmation Flow)
    print("\n2. Testing Booking Creation via Agent (2-turn confirmation)...")
    await asyncio.sleep(2)
    reply_2a = await run_agent_chat(
        system_prompt=system_prompt,
        user_message="I want to book Taj Exotica Resort & Spa, Goa from 2026-11-10 to 2026-11-15.",
        chat_history=[],
        user_id=user_id
    )
    print(f"Assistant Reply (Turn 1 - Asking for Confirmation):\n{reply_2a}")
    
    # Turn 2: User confirms
    from langchain_core.messages import HumanMessage, AIMessage
    turn_history = [
        HumanMessage(content="I want to book Taj Exotica Resort & Spa, Goa from 2026-11-10 to 2026-11-15."),
        AIMessage(content=reply_2a)
    ]
    
    await asyncio.sleep(2)
    reply_2b = await run_agent_chat(
        system_prompt=system_prompt,
        user_message="Yes, I confirm all details. Please create the booking now.",
        chat_history=turn_history,
        user_id=user_id
    )
    print(f"Assistant Reply (Turn 2 - Executing Booking):\n{reply_2b}")
    assert "Success" in reply_2b or "created" in reply_2b or "Booking ID" in reply_2b or "2026-11-10" in reply_2b or "confirmed" in reply_2b.lower(), "Booking creation failed"
    print("-> Booking Creation Test Passed!")
    
    # Verify in DB
    created_booking = await bookings_collection.find_one({"user_id": user_id, "destination": "Goa", "status": "active"})
    assert created_booking is not None, "Booking not found in DB"
    booking_id = str(created_booking["_id"])
    print(f"Verified created booking in DB: {booking_id}")
    
    # Test 3: Cancel Booking via Agent
    print("\n3. Testing Booking Cancellation via Agent...")
    await asyncio.sleep(2)
    reply_3 = await run_agent_chat(
        system_prompt=system_prompt,
        user_message=f"Please cancel my booking {booking_id}. I confirm I want to cancel it.",
        chat_history=[],
        user_id=user_id
    )
    print(f"Assistant Reply:\n{reply_3}")
    assert "cancelled" in reply_3.lower() or "success" in reply_3.lower(), "Booking cancellation failed"
    
    # Verify in DB
    updated_booking = await bookings_collection.find_one({"_id": created_booking["_id"]})
    assert updated_booking["status"] == "cancelled", "Booking status in DB should be 'cancelled'"
    print("-> Booking Cancellation Test Passed!")
    
    print("\n=== ALL PHASE D AGENTIC BOOKING TESTS PASSED PERFECTLY! ===")

if __name__ == "__main__":
    asyncio.run(test_phase_d())
