from fastapi import APIRouter, Depends, status
from typing import List, Optional
from app.schemas.group_trip_schema import GroupTripCreate, GroupTripResponse
from app.services import group_trip_service
from app.utils.dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=GroupTripResponse, status_code=status.HTTP_201_CREATED)
async def create_consensus_plan(
    request: GroupTripCreate,
    user_id: str = Depends(get_current_user)
):
    trip = await group_trip_service.create_group_trip_consensus(user_id, request)
    return GroupTripResponse(**trip)

@router.get("/", response_model=List[GroupTripResponse])
async def list_consensus_plans(
    status: Optional[str] = "active",
    user_id: str = Depends(get_current_user)
):
    trips = await group_trip_service.list_user_group_trips(user_id, status)
    return [GroupTripResponse(**t) for t in trips]

@router.get("/{trip_id}", response_model=GroupTripResponse)
async def get_consensus_plan(
    trip_id: str,
    user_id: str = Depends(get_current_user)
):
    trip = await group_trip_service.get_group_trip_details(user_id, trip_id)
    return GroupTripResponse(**trip)

@router.delete("/{trip_id}")
async def delete_consensus_plan(
    trip_id: str,
    user_id: str = Depends(get_current_user)
):
    await group_trip_service.delete_group_trip(user_id, trip_id)
    return {"detail": "Group trip consensus plan cancelled successfully"}
