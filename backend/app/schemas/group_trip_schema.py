from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class GroupMemberInput(BaseModel):
    name: str
    budget: float
    preferences: List[str]

class GroupTripCreate(BaseModel):
    trip_name: str
    destination: str
    num_nights: int = Field(default=3, ge=1)
    members: List[GroupMemberInput]

class RecommendedHotelOption(BaseModel):
    hotel_id: str
    name: str
    price_per_night: float
    rating: float
    description: str
    tags: List[str]
    image_url: Optional[str] = None
    per_person_cost: float
    total_cost: float
    score: int
    member_matches: Dict[str, List[str]]

class GroupTripResponse(BaseModel):
    id: str
    user_id: str
    trip_name: str
    destination: str
    num_nights: int
    members: List[GroupMemberInput]
    recommended_options: List[RecommendedHotelOption]
    reasoning: str
    created_at: str
    status: Optional[str] = "active"
