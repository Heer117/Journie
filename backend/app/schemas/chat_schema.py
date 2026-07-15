from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    message: str
    booking_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str