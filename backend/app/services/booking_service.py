import datetime
from bson import ObjectId
from fastapi import HTTPException, status
from app.db import hotels_collection, bookings_collection
from app.schemas.booking_schema import BookingCreate

async def list_hotels(destination: str = None) -> list[dict]:
    query = {}
    if destination:
        # Case-insensitive search
        query["destination"] = {"$regex": f"^{destination}$", "$options": "i"}
    
    cursor = hotels_collection.find(query)
    hotels = []
    async for hotel in cursor:
        hotel["id"] = str(hotel["_id"])
        hotels.append(hotel)
    return hotels

async def create_user_booking(user_id: str, booking_data: BookingCreate) -> dict:
    # Validate hotel_id format
    if not ObjectId.is_valid(booking_data.hotel_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid hotel ID format.",
        )
    
    # Check if hotel exists
    hotel = await hotels_collection.find_one({"_id": ObjectId(booking_data.hotel_id)})
    if not hotel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hotel not found.",
        )
    
    # Date validations
    try:
        start_dt = datetime.datetime.strptime(booking_data.start_date, "%Y-%m-%d")
        end_dt = datetime.datetime.strptime(booking_data.end_date, "%Y-%m-%d")
        passport_dt = datetime.datetime.strptime(booking_data.passport_expiry, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dates must be in YYYY-MM-DD format.",
        )
    
    today = datetime.date.today()
    if start_dt.date() < today:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-in date cannot be in the past.",
        )

    if start_dt >= end_dt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-out date must be strictly after check-in date.",
        )
        
    if passport_dt.date() <= today:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passport expiry date must be in the future.",
        )
        
    booking_doc = {
        "user_id": user_id,
        "hotel_id": booking_data.hotel_id,
        "hotel_name": hotel["name"],
        "destination": booking_data.destination,
        "start_date": booking_data.start_date,
        "end_date": booking_data.end_date,
        "passport_expiry": booking_data.passport_expiry,
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    
    result = await bookings_collection.insert_one(booking_doc)
    booking_doc["id"] = str(result.inserted_id)
    return booking_doc

async def get_user_bookings(user_id: str) -> list[dict]:
    cursor = bookings_collection.find({"user_id": user_id}).sort("created_at", -1)
    bookings = []
    async for booking in cursor:
        booking["id"] = str(booking["_id"])
        bookings.append(booking)
    return bookings
