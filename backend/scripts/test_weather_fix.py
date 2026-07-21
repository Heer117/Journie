import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.llm_service import get_weather

async def main():
    print("--- Testing Fixed get_weather Geocoding ---")
    
    res_bali = await get_weather.ainvoke({"destination": "Bali", "date": "2026-07-22"})
    print("\nWeather for Bali:")
    print(res_bali)

    res_goa = await get_weather.ainvoke({"destination": "Goa", "date": "2026-07-22"})
    print("\nWeather for Goa:")
    print(res_goa)

if __name__ == "__main__":
    asyncio.run(main())
