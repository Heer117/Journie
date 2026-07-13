from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
 
# One client for the whole app's lifetime — created once at import time.
# Motor manages a connection pool internally, so we don't reconnect per-request.
client = AsyncIOMotorClient(settings.mongodb_uri)
db = client[settings.mongodb_db_name]
 
# Collections — one line per collection keeps route/service files clean,
# they just do `from app.db import users_collection` etc.
users_collection = db["users"]
hotels_collection = db["hotels"]
bookings_collection = db["bookings"]
conversations_collection = db["conversations"]
group_trips_collection = db["group_trips"]
document_checks_collection = db["document_checks"]
live_assist_logs_collection = db["live_assist_logs"]