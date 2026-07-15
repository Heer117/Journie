import datetime
from bson import ObjectId
from fastapi import HTTPException, status
from app.db import hotels_collection, group_trips_collection
from app.schemas.group_trip_schema import GroupTripCreate
from app.services.llm_service import get_chat_completion

async def create_group_trip_consensus(user_id: str, trip_data: GroupTripCreate) -> dict:
    # 1. Fetch all hotels in the given destination
    query = {"destination": {"$regex": f"^{trip_data.destination}$", "$options": "i"}}
    cursor = hotels_collection.find(query)
    hotels = []
    async for hotel in cursor:
        hotel["id"] = str(hotel["_id"])
        hotels.append(hotel)

    recommended_options = []
    num_members = len(trip_data.members)
    
    if num_members == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group trip must have at least one member.",
        )

    # 2. Filter and score hotels
    for hotel in hotels:
        total_cost = hotel["price_per_night"] * trip_data.num_nights
        per_person_cost = total_cost / num_members
        
        # Check if hotel satisfies ALL members' budgets
        all_budgets_satisfied = True
        member_matches = {}
        score = 0
        
        for member in trip_data.members:
            if per_person_cost > member.budget:
                all_budgets_satisfied = False
                break
            
            # Calculate overlapping preference tags
            matches = list(set(member.preferences).intersection(set(hotel.get("tags", []))))
            member_matches[member.name] = matches
            score += len(matches)
            
        if all_budgets_satisfied:
            recommended_options.append({
                "hotel_id": hotel["id"],
                "name": hotel["name"],
                "price_per_night": hotel["price_per_night"],
                "rating": hotel["rating"],
                "description": hotel["description"],
                "tags": hotel.get("tags", []),
                "image_url": hotel.get("image_url"),
                "per_person_cost": per_person_cost,
                "total_cost": total_cost,
                "score": score,
                "member_matches": member_matches
            })

    # 3. Sort options: score (desc), rating (desc), price_per_night (asc)
    recommended_options.sort(
        key=lambda x: (-x["score"], -x["rating"], x["price_per_night"])
    )

    # 4. Generate AI reasoning using Groq LLM
    members_text = "\n".join(
        f"- {m.name}: Budget ${m.budget}, Preferences {m.preferences}"
        for m in trip_data.members
    )
    
    if recommended_options:
        # Include top 3 options in prompt context
        top_options = recommended_options[:3]
        options_text = ""
        for idx, opt in enumerate(top_options, 1):
            options_text += f"{idx}. {opt['name']} ({opt['rating']} stars, ${opt['price_per_night']}/night, total split cost per person: ${opt['per_person_cost']:.2f}). Matches:\n"
            for m_name, m_tags in opt['member_matches'].items():
                options_text += f"   - {m_name}: matched tags {m_tags}\n"
                
        prompt = f"""You are Journie, a professional AI travel booking assistant. 
Write a cohesive "Why this works" explanation of the recommended hotel options for a group trip consensus plan.

Destination: {trip_data.destination}
Nights: {trip_data.num_nights}
Members and Budgets/Preferences:
{members_text}

Recommended Hotels:
{options_text}

Rules:
1. Do NOT use any emojis anywhere in the response.
2. Address the group as a whole.
3. Explain how the recommendations fit everyone's budget.
4. Highlight how the hotel features/tags match the members' preferences (be specific about who gets what they wanted).
5. Keep the tone professional, friendly, and concise (under 200 words).
"""
    else:
        prompt = f"""You are Journie, a professional AI travel booking assistant.
Explain to a group of travelers why no hotels in {trip_data.destination} satisfied all of their budget requirements.

Destination: {trip_data.destination}
Nights: {trip_data.num_nights}
Members and Budgets/Preferences:
{members_text}

Rules:
1. Do NOT use any emojis anywhere in the response.
2. Explain clearly that the hotel costs split per person exceeded at least one member's budget.
3. Suggest practical alternatives (e.g., choose a different destination, reduce the number of nights, or adjust individual budgets).
4. Keep the tone helpful, professional, and concise (under 150 words).
"""

    messages = [{"role": "user", "content": prompt}]
    
    try:
        reasoning = get_chat_completion(messages)
    except Exception as e:
        print(f"Error calling LLM: {e}")
        reasoning = "Failed to generate AI reasoning due to an external service issue, but your consensus options have been successfully calculated."

    # 5. Save to database
    trip_doc = {
        "user_id": user_id,
        "trip_name": trip_data.trip_name,
        "destination": trip_data.destination,
        "num_nights": trip_data.num_nights,
        "members": [m.model_dump() for m in trip_data.members],
        "recommended_options": recommended_options,
        "reasoning": reasoning,
        "status": "active",
        "created_at": datetime.datetime.utcnow().isoformat()
    }

    result = await group_trips_collection.insert_one(trip_doc)
    trip_doc["id"] = str(result.inserted_id)
    if "_id" in trip_doc:
        del trip_doc["_id"]
        
    return trip_doc

async def list_user_group_trips(user_id: str, status: str = "active") -> list[dict]:
    query = {"user_id": user_id}
    if status == "active":
        query["status"] = {"$in": ["active", None]}
    elif status == "cancelled":
        query["status"] = "cancelled"
    # if status is "all", retrieve all trips without status filter
    
    cursor = group_trips_collection.find(query).sort("created_at", -1)
    trips = []
    async for trip in cursor:
        trip["id"] = str(trip["_id"])
        del trip["_id"]
        trips.append(trip)
    return trips

async def get_group_trip_details(user_id: str, trip_id: str) -> dict:
    if not ObjectId.is_valid(trip_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid group trip ID format."
        )
    trip = await group_trips_collection.find_one({"_id": ObjectId(trip_id), "user_id": user_id})
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group trip plan not found."
        )
    trip["id"] = str(trip["_id"])
    del trip["_id"]
    return trip

async def delete_group_trip(user_id: str, trip_id: str) -> None:
    if not ObjectId.is_valid(trip_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid group trip ID format."
        )
        
    trip = await group_trips_collection.find_one({
        "_id": ObjectId(trip_id),
        "user_id": user_id
    })
    
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group trip plan not found."
        )
        
    # Soft delete: update status to cancelled
    await group_trips_collection.update_one(
        {"_id": ObjectId(trip_id)},
        {"$set": {"status": "cancelled"}}
    )
