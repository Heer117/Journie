import datetime
import json
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

    # 2. Filter and score hotels deterministically first (safety floor + base fallback)
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
            
            # Calculate overlapping preference tags (base overlap for safety fallback)
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

    # 3. Call LLM for AI-driven scoring & semantic matching or compromise suggestions
    members_input = [
        {"name": m.name, "budget": m.budget, "preferences": m.preferences}
        for m in trip_data.members
    ]
    
    # Prepare information for all hotels in the destination (needed for compromise suggestions or general context)
    all_hotels_input = [
        {
            "hotel_id": h["id"],
            "name": h["name"],
            "price_per_night": h["price_per_night"],
            "rating": h["rating"],
            "description": h["description"],
            "tags": h.get("tags", [])
        }
        for h in hotels
    ]
    
    if recommended_options:
        candidates_input = [
            {
                "hotel_id": opt["hotel_id"],
                "name": opt["name"],
                "price_per_night": opt["price_per_night"],
                "rating": opt["rating"],
                "description": opt["description"],
                "tags": opt["tags"]
            }
            for opt in recommended_options
        ]
        
        system_prompt = """You are Journie, a professional AI travel booking assistant.
Your job is to analyze group travel options and evaluate how well they match the group members' budgets and preferences.
You must output a single valid JSON object. Do not include any markdown block formatting (like ```json or ```) or other text outside the JSON object.

The JSON object MUST follow this schema:
{
  "recommendations": [
    {
      "hotel_id": "string",
      "score": integer,
      "member_matches": {
        "memberName1": ["matched_pref1", "matched_pref2"],
        "memberName2": []
      }
    }
  ],
  "reasoning": "string"
}

Rules:
1. Do NOT use any emojis in the reasoning or any other text.
2. In the "recommendations" list, ONLY include hotels that are provided in the candidate list.
3. For each hotel, evaluate the overlap between its characteristics (description, name, tags) and each group member's preferences.
   Handle ambiguous or semantic matches (e.g. traveler prefers "swimming pool" and hotel has "pool", or traveler prefers "quiet" and hotel has "peaceful", or traveler prefers "luxury" and hotel has high rating/premium services).
   Identify matched preferences/concepts as a list of strings for each member.
   The "score" should be the total number of matched preferences across all members.
4. The "reasoning" should be a cohesive, friendly, and professional explanation (under 200 words) addressing the group as a whole.
   Explain how the options fit everyone's budget, highlight how features match preferences (be specific about who gets what), and maintain a professional travel agent tone.
"""
        user_content = f"""Destination: {trip_data.destination}
Nights: {trip_data.num_nights}
Members: {json.dumps(members_input)}
Candidate Hotels: {json.dumps(candidates_input)}
"""
    else:
        # No candidate hotels satisfied everyone's budgets
        system_prompt = """You are Journie, a professional AI travel booking assistant.
Your job is to analyze group travel options when no hotel perfectly fits everyone's budget, and suggest practical compromises or alternatives.
You must output a single valid JSON object. Do not include any markdown block formatting (like ```json or ```) or other text outside the JSON object.

The JSON object MUST follow this schema:
{
  "recommendations": [],
  "reasoning": "string"
}

Rules:
1. Do NOT use any emojis in the reasoning or any other text.
2. The "recommendations" list must be empty [].
3. The "reasoning" should explain to the group why no hotels satisfy all budgets, and suggest specific compromises (e.g. which hotels would fit if a specific member adjusted their budget, or how reducing the stay duration from X to a lower number of nights would make certain hotels fit). Keep the tone helpful, professional, and concise (under 150 words).
"""
        user_content = f"""Destination: {trip_data.destination}
Nights: {trip_data.num_nights}
Members: {json.dumps(members_input)}
Candidate Hotels: [] (No hotels satisfy the hard budget constraints of all members)
All Hotels in Destination: {json.dumps(all_hotels_input)}
"""
        
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]
    
    reasoning = ""
    try:
        raw_reply = get_chat_completion(messages)
        # Parse JSON reply resiliently
        reply_content = raw_reply.strip()
        if reply_content.startswith("```"):
            # strip backticks and optional json language specifier
            lines = reply_content.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            reply_content = "\n".join(lines).strip()
            
        data = json.loads(reply_content)
        reasoning = data.get("reasoning", "")
        
        # If we had candidates, update their scores and member_matches based on LLM output
        if recommended_options and "recommendations" in data:
            rec_map = {r["hotel_id"]: r for r in data["recommendations"] if "hotel_id" in r}
            for opt in recommended_options:
                h_id = opt["hotel_id"]
                if h_id in rec_map:
                    # Update with LLM semantic match data
                    opt["score"] = rec_map[h_id].get("score", opt["score"])
                    opt["member_matches"] = rec_map[h_id].get("member_matches", opt["member_matches"])
                    
            # Re-sort options based on LLM scores (desc), rating (desc), price (asc)
            recommended_options.sort(
                key=lambda x: (-x["score"], -x["rating"], x["price_per_night"])
            )
            
    except Exception as e:
        print(f"Error calling or parsing LLM for group trip consensus: {e}")
        # Fallback to standard deterministic reasoning if LLM fails or doesn't return JSON
        if not reasoning:
            members_text = "\n".join(
                f"- {m.name}: Budget ${m.budget}, Preferences {m.preferences}"
                for m in trip_data.members
            )
            if recommended_options:
                top_options = recommended_options[:3]
                options_text = ""
                for idx, opt in enumerate(top_options, 1):
                    options_text += f"{idx}. {opt['name']} ({opt['rating']} stars, ${opt['price_per_night']}/night, total split cost per person: ${opt['per_person_cost']:.2f}). Matches:\n"
                    for m_name, m_tags in opt['member_matches'].items():
                        options_text += f"   - {m_name}: matched tags {m_tags}\n"
                        
                fallback_prompt = f"""You are Journie, a professional AI travel booking assistant. 
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
                fallback_prompt = f"""You are Journie, a professional AI travel booking assistant.
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
            try:
                reasoning = get_chat_completion([{"role": "user", "content": fallback_prompt}])
            except Exception as fb_err:
                print(f"Fallback LLM call failed: {fb_err}")
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
