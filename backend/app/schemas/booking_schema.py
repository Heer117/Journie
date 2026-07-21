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

DOMESTIC_DESTINATIONS = {"goa", "manali", "jaipur", "udaipur", "kerala", "rishikesh", "andaman", "lakshadweep", "ladakh", "darjeeling"}

class BookingCreate(BaseModel):
    hotel_id: str
    destination: str
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    passport_expiry: Optional[str] = "N/A"  # YYYY-MM-DD or N/A
    booked_for: Optional[BookedForInput] = None

    @field_validator('start_date', 'end_date')
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format.")
        return v

    @field_validator('passport_expiry')
    @classmethod
    def validate_passport_format(cls, v: Optional[str]) -> str:
        if not v or v.strip().upper() == "N/A":
            return "N/A"
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Passport expiry date must be in YYYY-MM-DD format.")
        return v

    @model_validator(mode='after')
    def validate_dates(self) -> 'BookingCreate':
        try:
            start = datetime.strptime(self.start_date, "%Y-%m-%d").date()
            end = datetime.strptime(self.end_date, "%Y-%m-%d").date()
        except ValueError:
            return self

        today = date.today()
        if start < today:
            raise ValueError("Check-in date cannot be in the past.")
        if end <= start:
            raise ValueError("Check-out date must be strictly after check-in date.")

        is_domestic = self.destination.strip().lower() in DOMESTIC_DESTINATIONS

        if is_domestic:
            self.passport_expiry = "N/A"
        else:
            if not self.passport_expiry or self.passport_expiry == "N/A":
                raise ValueError("Passport expiry date is required for international travel.")
            try:
                passport = datetime.strptime(self.passport_expiry, "%Y-%m-%d").date()
                if passport <= today:
                    raise ValueError("Passport expiry date must be in the future.")
            except ValueError as e:
                if "required" in str(e) or "future" in str(e):
                    raise e
                raise ValueError("Invalid passport expiry date.")
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
