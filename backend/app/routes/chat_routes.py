from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.llm_service import run_agent_chat, deserialize_messages, message_to_dict
from langchain_core.messages import HumanMessage, AIMessage
from app.db import conversations_collection, bookings_collection
from app.utils.dependencies import get_current_user

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, user_id: str = Depends(get_current_user)):
    conversation = await conversations_collection.find_one({"user_id": user_id})

    if conversation is None:
        history = []
    else:
        history = conversation.get("messages", [])

    # Deserialize message history to LangChain messages
    langchain_history = deserialize_messages(history)

    system_content = (
        "You are Journie, a helpful, grounded AI travel assistant. "
        "Provide clear and professional support. Structure your responses beautifully using standard Markdown. "
        "Use bolding to highlight key names, places, dates, and terms. Use clean bullet points or numbered lists "
        "when listing items, itineraries, options, or instructions. Use section headers for longer explanations. "
        "NEVER use any emojis in your response."
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
            "and dates. Structure your responses beautifully using standard Markdown. Use bolding to highlight key names, "
            "places, dates, and terms. Use clean bullet points or numbered lists when listing items, itineraries, options, "
            "or instructions. Use section headers for longer explanations. NEVER use any emojis in your response."
        )

    # Run agent executor
    reply_text = run_agent_chat(
        system_prompt=system_content,
        user_message=request.message,
        chat_history=langchain_history,
    )

    # Add the current exchange to conversation memory
    langchain_history.append(HumanMessage(content=request.message))
    langchain_history.append(AIMessage(content=reply_text))

    # Serialize back to MongoDB format
    serialized_history = [message_to_dict(msg) for msg in langchain_history]

    await conversations_collection.update_one(
        {"user_id": user_id},
        {"$set": {"messages": serialized_history}},
        upsert=True,
    )

    return ChatResponse(reply=reply_text)