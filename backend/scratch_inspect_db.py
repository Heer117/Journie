import asyncio
import os
import sys

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db import (
    users_collection,
    hotels_collection,
    bookings_collection,
    conversations_collection,
    group_trips_collection,
    document_checks_collection,
    live_assist_logs_collection,
)

async def main():
    print("--- Collection Counts ---")
    for name, coll in [
        ("users", users_collection),
        ("hotels", hotels_collection),
        ("bookings", bookings_collection),
        ("conversations", conversations_collection),
        ("group_trips", group_trips_collection),
        ("document_checks", document_checks_collection),
        ("live_assist_logs", live_assist_logs_collection),
    ]:
        cnt = await coll.count_documents({})
        print(f"{name}: {cnt}")
        if cnt > 0:
            doc = await coll.find_one({})
            print(f"  Sample fields: {list(doc.keys())}")
            if name == "bookings":
                print(f"  Booking doc: {doc}")
            if name == "document_checks":
                print(f"  Document Check doc: {doc}")

if __name__ == "__main__":
    asyncio.run(main())
