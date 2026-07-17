from pydantic import BaseModel, field_validator, model_validator
from typing import List, Optional
from datetime import datetime, date

class HotelResponse(BaseModel):
    id: str
    name: str
    destination: str
    price_per_night: float
    rating: float
    description: str
    tags: List[str]

class BookedForInput(BaseModel):
    name: str
    phone: str
    relation: Optional[str] = None

class BookingCreate(BaseModel):
    hotel_id: str
    destination: str
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    passport_expiry: str  # YYYY-MM-DD
    booked_for: Optional[BookedForInput] = None

    @field_validator('start_date', 'end_date', 'passport_expiry')
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format.")
        return v

    @model_validator(mode='after')
    def validate_dates(self) -> 'BookingCreate':
        try:
            start = datetime.strptime(self.start_date, "%Y-%m-%d").date()
            end = datetime.strptime(self.end_date, "%Y-%m-%d").date()
            passport = datetime.strptime(self.passport_expiry, "%Y-%m-%d").date()
        except ValueError:
            # Let the field validators handle format issues
            return self

        today = date.today()
        if start < today:
            raise ValueError("Check-in date cannot be in the past.")
        if end <= start:
            raise ValueError("Check-out date must be strictly after check-in date.")
        if passport <= today:
            raise ValueError("Passport expiry date must be in the future.")
        return self

class DocumentCheckResponse(BaseModel):
    status: str
    reason: str

class BookingResponse(BaseModel):
    id: str
    user_id: str
    hotel_id: str
    hotel_name: str
    destination: str
    start_date: str
    end_date: str
    passport_expiry: str
    created_at: str
    status: Optional[str] = "active"
    document_check: Optional[DocumentCheckResponse] = None
    booked_for: Optional[BookedForInput] = None
