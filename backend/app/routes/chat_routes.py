from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.llm_service import get_chat_completion
from app.db import conversations_collection, bookings_collection
from app.utils.dependencies import get_current_user

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, user_id: str = Depends(get_current_user)):
    conversation = await conversations_collection.find_one({"user_id": user_id})

    if conversation is None:
        history = []
    else:
        history = conversation["messages"]

    history.append({"role": "user", "content": request.message})

    # Prepare messages to send to the LLM
    messages_to_send = []
    
    system_content = (
        "You are Journie, a helpful, grounded AI travel assistant. "
        "Provide clear and professional support. NEVER use any emojis in your response."
    )
    
    if request.booking_id:
        if not ObjectId.is_valid(request.booking_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid booking ID format.",
            )
            
        booking = await bookings_collection.find_one({
            "_id": ObjectId(request.booking_id),
            "user_id": user_id
        })
        
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found.",
            )
            
        system_content = (
            "You are Journie, a helpful, grounded AI travel assistant. The user is asking about their booking context:\n"
            f"- Destination: {booking['destination']}\n"
            f"- Dates: {booking['start_date']} to {booking['end_date']}\n"
            f"- Hotel: {booking['hotel_name']}\n\n"
            "Provide grounded assistance for this trip context. Specifically, address matters like delays, "
            "lost luggage, medical emergencies, local transport, and disruptions in the context of this destination "
            "and dates. NEVER use any emojis in your response."
        )
        
    messages_to_send.append({"role": "system", "content": system_content})
    messages_to_send.extend(history)

    reply_text = get_chat_completion(messages_to_send)

    history.append({"role": "assistant", "content": reply_text})

    await conversations_collection.update_one(
        {"user_id": user_id},
        {"$set": {"messages": history}},
        upsert=True,
    )

    return ChatResponse(reply=reply_text)