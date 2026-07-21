import asyncio
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.llm_service import get_weather, search_places, run_agent_chat
from langchain_core.messages import HumanMessage

async def main():
    print("--- Testing Phase C Agent Tools ---")

    # 1. Test get_weather tool
    print("\n1. Testing get_weather tool...")
    weather_res = await get_weather.ainvoke({"destination": "Tokyo", "date": "2026-09-15"})
    print("get_weather output:")
    print(weather_res)
    assert "Tokyo" in weather_res, "Expected destination 'Tokyo' in weather output"

    # 2. Test search_places tool
    print("\n2. Testing search_places tool...")
    places_res = await search_places.ainvoke({"query": "top attractions in Tokyo"})
    print("search_places output:")
    print(places_res[:300] + "...")
    assert len(places_res) > 0, "Expected non-empty search places output"

    # 3. Test run_agent_chat with tool invocation
    print("\n3. Testing run_agent_chat tool invocation...")
    system_prompt = "You are Journie, an AI travel assistant. Use available tools to answer questions accurately."
    
    chat_reply = await run_agent_chat(
        system_prompt=system_prompt,
        user_message="What's the weather forecast for Paris on 2026-10-01?",
        chat_history=[],
        user_id="test_user_123"
    )
    print("\nAgent chat reply:")
    print(chat_reply)
    assert "Paris" in chat_reply, "Expected Paris in reply"

    print("\n--- ALL PHASE C TOOL TESTS PASSED SUCCESSFULLY! ---")

if __name__ == "__main__":
    asyncio.run(main())
