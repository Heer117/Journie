import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import httpx
from app.config import settings

async def test_serpapi_weather():
    api_key = getattr(settings, "serpapi_api_key", None) or os.environ.get("SERPAPI_API_KEY")
    print(f"SerpAPI Key present: {bool(api_key)}")
    
    if api_key:
        url = "https://serpapi.com/search.json"
        params = {
            "engine": "google",
            "q": "Ubud Bali weather",
            "api_key": api_key
        }
        async with httpx.AsyncClient() as client:
            res = await client.get(url, params=params, timeout=10.0)
            if res.status_code == 200:
                data = res.json()
                print("Answer box keys:", data.get("answer_box", {}).keys())
                print("Answer box:", data.get("answer_box"))

if __name__ == "__main__":
    asyncio.run(test_serpapi_weather())
