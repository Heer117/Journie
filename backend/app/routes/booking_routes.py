from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from app.schemas.booking_schema import BookingCreate, BookingResponse, HotelResponse
from app.services import booking_service
from app.utils.dependencies import get_current_user

router = APIRouter()

@router.get("/hotels", response_model=List[HotelResponse])
async def get_hotels(destination: Optional[str] = Query(None)):
    hotels = await booking_service.list_hotels(destination)
    return [HotelResponse(**h) for h in hotels]

@router.post("/", response_model=BookingResponse)
async def create_booking(request: BookingCreate, user_id: str = Depends(get_current_user)):
    booking = await booking_service.create_user_booking(user_id, request)
    return BookingResponse(**booking)

@router.get("/", response_model=List[BookingResponse])
async def get_bookings(status: Optional[str] = "active", user_id: str = Depends(get_current_user)):
    bookings = await booking_service.get_user_bookings(user_id, status)
    return [BookingResponse(**b) for b in bookings]

@router.delete("/{booking_id}")
async def delete_booking(booking_id: str, user_id: str = Depends(get_current_user)):
    await booking_service.delete_user_booking(user_id, booking_id)
    return {"detail": "Booking cancelled successfully"}
