import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db import group_trips_collection

async def main():
    trips = await group_trips_collection.find().sort("created_at", -1).to_list(length=5)
    print(f"Found {len(trips)} recent group trip documents:")
    for idx, t in enumerate(trips, 1):
        print(f"\n--- Trip {idx} ---")
        print(f"ID: {t.get('_id') or t.get('id')}")
        print(f"Name: {t.get('trip_name')}")
        print(f"Destination: {t.get('destination')}")
        print(f"Nights: {t.get('num_nights')}")
        print(f"Members: {t.get('members')}")
        print(f"Reasoning: {t.get('reasoning')[:100]}...")
        options = t.get('recommended_options', [])
        print(f"Options count: {len(options)}")
        for opt in options:
            print(f"  Hotel: {opt.get('name')}, Per Person: {opt.get('per_person_cost')}, Total: {opt.get('total_cost')}, Price/Night: {opt.get('price_per_night')}")

if __name__ == "__main__":
    asyncio.run(main())
