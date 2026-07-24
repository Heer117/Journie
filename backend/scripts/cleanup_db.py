import asyncio
import sys
import os
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

async def main():
    parser = argparse.ArgumentParser(description="Cleanup Journie MongoDB database.")
    parser.add_argument(
        "--keep",
        type=str,
        default="demo@journie.com,rads@gmail.com,test@example.com",
        help="Comma-separated list of emails to keep (default: demo@journie.com,rads@gmail.com,test@example.com)"
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompt"
    )
    args = parser.parse_args()

    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.mongodb_db_name]

    # Parse emails to keep
    emails_to_keep = [e.strip().lower() for e in args.keep.split(",") if e.strip()]

    # Fetch all users
    users = await db["users"].find().to_list(None)
    if not users:
        print("No users found in the database.")
        return

    print("\n--- Current Users in Database ---")
    for idx, u in enumerate(users):
        keep_marker = " [KEEP]" if u.get("email", "").lower() in emails_to_keep else ""
        print(f"{idx + 1}. Email: {u.get('email')} | ID: {u.get('_id')}{keep_marker}")

    users_to_delete = [u for u in users if u.get("email", "").lower() not in emails_to_keep]
    ids_to_delete = [u["_id"] for u in users_to_delete]
    emails_deleted = [u["email"] for u in users_to_delete]

    if not ids_to_delete:
        print("\nNo users to delete based on the keep list.")
        return

    print(f"\nPlan: Delete {len(users_to_delete)} users (keeping: {emails_to_keep}).")
    print(f"Emails to delete: {emails_deleted}")

    if not args.yes:
        confirm = input("\nProceed with deleting these users and all their associated bookings/chats? (y/n): ").strip().lower()
        if confirm != "y":
            print("Aborted.")
            return

    # Delete related documents
    user_res = await db["users"].delete_many({"_id": {"$in": ids_to_delete}})
    booking_res = await db["bookings"].delete_many({"user_id": {"$in": [str(i) for i in ids_to_delete]}})
    conv_res = await db["conversations"].delete_many({"user_id": {"$in": [str(i) for i in ids_to_delete]}})
    doc_res = await db["document_checks"].delete_many({"user_id": {"$in": [str(i) for i in ids_to_delete]}})

    print(f"\n--- Cleanup Completed Successfully ---")
    print(f"Deleted {user_res.deleted_count} user accounts.")
    print(f"Deleted {booking_res.deleted_count} booking records.")
    print(f"Deleted {conv_res.deleted_count} conversation logs.")
    print(f"Deleted {doc_res.deleted_count} document checks.")

if __name__ == "__main__":
    asyncio.run(main())
