import datetime
from bson import ObjectId
from fastapi import HTTPException, status
from app.db import hotels_collection, bookings_collection, document_checks_collection
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
        
    # Date overlap check: only if booking for self
    if not booking_data.booked_for:
        active_bookings_cursor = bookings_collection.find({
            "user_id": user_id,
            "status": {"$in": ["active", None]}
        })
        async for b in active_bookings_cursor:
            try:
                existing_start = datetime.datetime.strptime(b["start_date"], "%Y-%m-%d").date()
                existing_end = datetime.datetime.strptime(b["end_date"], "%Y-%m-%d").date()
            except ValueError:
                continue
            
            if start_dt.date() < existing_end and end_dt.date() > existing_start:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"You already have a booking from {b['start_date']} to {b['end_date']} that overlaps these dates."
                )

    booking_doc = {
        "user_id": user_id,
        "hotel_id": booking_data.hotel_id,
        "hotel_name": hotel["name"],
        "destination": booking_data.destination,
        "start_date": booking_data.start_date,
        "end_date": booking_data.end_date,
        "passport_expiry": booking_data.passport_expiry,
        "status": "active",
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    
    if booking_data.booked_for:
        booking_doc["booked_for"] = booking_data.booked_for.model_dump()
    
    result = await bookings_collection.insert_one(booking_doc)
    booking_id = str(result.inserted_id)
    booking_doc["id"] = booking_id
    
    # Run the document check and attach it
    from app.services.document_check_service import perform_document_check
    check = await perform_document_check(
        user_id=user_id,
        booking_id=booking_id,
        destination=booking_data.destination,
        end_date_str=booking_data.end_date,
        passport_expiry_str=booking_data.passport_expiry
    )
    booking_doc["document_check"] = check
    return booking_doc

async def get_user_bookings(user_id: str, status: str = "active") -> list[dict]:
    query = {"user_id": user_id}
    if status == "active":
        query["status"] = {"$in": ["active", None]}
    elif status == "cancelled":
        query["status"] = "cancelled"
    # if status is "all", we retrieve all bookings without status filter
    
    cursor = bookings_collection.find(query).sort("created_at", -1)
    bookings = []
    async for booking in cursor:
        booking["id"] = str(booking["_id"])
        
        # Load and attach document check (fall back to compute if missing) only if not cancelled
        if booking.get("status") != "cancelled":
            from app.services.document_check_service import get_booking_document_check
            check = await get_booking_document_check(user_id, booking["id"], booking)
            booking["document_check"] = check
        else:
            booking["document_check"] = None
        
        bookings.append(booking)
    return bookings

async def delete_user_booking(user_id: str, booking_id: str) -> None:
    if not ObjectId.is_valid(booking_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid booking ID format.",
        )
        
    booking = await bookings_collection.find_one({
        "_id": ObjectId(booking_id),
        "user_id": user_id
    })
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found.",
        )
        
    # Soft delete: update status to cancelled
    await bookings_collection.update_one(
        {"_id": ObjectId(booking_id)},
        {"$set": {"status": "cancelled"}}
    )
    
    # Clean up associated document check entries for that booking
    await document_checks_collection.delete_many({"booking_id": booking_id})
