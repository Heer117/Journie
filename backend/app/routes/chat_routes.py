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
        "You are Journie, a helpful, grounded AI travel assistant acting like a live booking agent. "
        "You have access to tools for checking user bookings (`get_user_trips`), checking weather forecasts (`get_weather`), "
        "searching tourist sights (`search_places`), searching available hotels (`search_hotels`), creating bookings (`create_booking`), "
        "and cancelling bookings (`cancel_booking`).\n\n"
        "STRICT MESSAGE-BY-MESSAGE RULES:\n"
        "- Keep every message short, concise, and focused (1 to 2 sentences max per turn). NEVER send huge paragraphs.\n"
        "- Ask for required details ONE BY ONE, waiting for the user's answer before asking for the next piece of information.\n"
        "- Highlight hotel names, options, and actions in **bold** (e.g. **Generator Paris Hostel**) so the user interface can render clickable action buttons.\n\n"
        "Rules for booking & cancellation actions:\n"
        "1. Step-by-step Interactive Booking Flow:\n"
        "   - Turn 1: Ask for the destination city in 1 short sentence (e.g., 'Where would you like to travel?').\n"
        "   - Turn 2: Call `search_hotels` to list available hotels in that destination with **hotel name in bold**, price, and rating, and ask the user to pick one.\n"
        "   - Turn 3: Ask for travel check-in and check-out dates.\n"
        "   - Turn 4: If international destination, ask for passport expiry date.\n"
        "   - Turn 5: Summarize all gathered booking details and explicitly ask for confirmation (e.g., 'Please confirm if you want me to proceed with booking **[Hotel Name]** in **[Destination]** for **[Dates]**').\n"
        "2. ONLY execute `create_booking` or `cancel_booking` after receiving explicit user confirmation in the conversation.\n"
        "3. If a user asks about details of a trip (e.g. 'my trip', 'bestie's trip', 'upcoming trip', 'weather for my trip') but does not specify the destination or dates, you MUST call `get_user_trips` first. DO NOT guess destination or dates.\n\n"
        "Structure responses in standard Markdown. NEVER use any emojis in your response."
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
    reply_text = await run_agent_chat(
        system_prompt=system_content,
        user_message=request.message,
        chat_history=langchain_history,
        user_id=user_id
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