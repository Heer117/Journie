import asyncio
import httpx

async def test():
    destinations = ["Bali", "Bali, Indonesia", "Ubud", "Goa", "Goa, India"]
    async with httpx.AsyncClient() as client:
        for dest in destinations:
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={dest}&count=3&language=en&format=json"
            res = await client.get(geo_url)
            data = res.json()
            results = data.get("results", [])
            print(f"\nQuery: '{dest}'")
            for r in results:
                name = r.get('name', '').encode('ascii', 'ignore').decode('ascii')
                country = r.get('country', '').encode('ascii', 'ignore').decode('ascii')
                print(f"  -> {name}, {country} (Lat: {r.get('latitude')}, Lon: {r.get('longitude')}, Pop: {r.get('population', 0)})")

if __name__ == "__main__":
    asyncio.run(test())
