from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.llm_service import run_agent_chat, deserialize_messages, message_to_dict, booking_modified_var
from langchain_core.messages import HumanMessage, AIMessage
from app.db import conversations_collection, bookings_collection
from app.utils.dependencies import get_current_user

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, user_id: str = Depends(get_current_user)):
    clean_msg = (request.message or "").strip().lower()
    if clean_msg in ["reset", "/reset", "clear", "clear chat", "reset chat", "clear history"]:
        await conversations_collection.delete_one({"user_id": user_id})
        return ChatResponse(reply="Your chat history has been successfully reset. How can I help you today?", booking_updated=False)

    conversation = await conversations_collection.find_one({"user_id": user_id})

    if conversation is None:
        history = []
    else:
        # Limit history to the last 12 messages (6 turns) to avoid hitting Groq API TPM limits (6k limit)
        history = conversation.get("messages", [])[-12:]

    # Deserialize message history to LangChain messages
    langchain_history = deserialize_messages(history)

    system_content = (
        "You are Journie, a warm, professional AI travel agent. "
        "You have access to tools for checking user bookings (`get_user_trips`), checking weather forecasts (`get_weather`), "
        "searching tourist sights (`search_places`), searching available hotels (`search_hotels`), creating bookings (`create_booking`), "
        "and cancelling bookings (`cancel_booking`).\n\n"
        "CONVERSATIONAL AGENT INSTRUCTIONS:\n"
        "0. NO HALLUCINATION / MANDATORY TOOL CALLS: You are STRICTLY FORBIDDEN from guessing, making up, or generating mock trip lists, booking details, weather forecasts, or hotel lists. If the user asks about their trips, upcoming travels, weather, or hotels, you MUST call the appropriate tool (`get_user_trips`, `get_weather`, `search_hotels`) to retrieve the real database data. Never output fake JSON/markdown lists or tool descriptions as your text reply.\n"
        "1. TONE AND LENGTH: Always respond in a warm, helpful, and professional travel assistant tone. "
        "Keep your comments concise and direct. During the step-by-step information gathering turns, ask exactly one question at a time. "
        "However, when displaying data fetched from tools (such as hotel lists, booking lists, weather details, or attraction search results), "
        "you MUST print the full fetched details clearly in structured markdown, and then follow up with a single concise guiding question (e.g. 'Which of these hotels would you like to book?'). "
        "NEVER hide or summarize fetched trip lists or weather details into a generic question.\n"
        "2. ONLY ONE TOOL CALL PER TURN: You are strictly limited to invoking a maximum of ONE tool call per conversational turn. "
        "Do NOT call multiple tools or try to chain multiple calls in parallel. If you need more information, ask the user or call one tool first.\n"
        "3. MANDATORY HOTEL SEARCH ON DESTINATION INPUT: When the user mentions a destination city (e.g. 'Dubai', 'Udaipur', 'Paris', 'Goa', 'Bali', 'Manali', etc.), "
        "you MUST immediately invoke `search_hotels` for that destination to fetch available hotels. DO NOT reply conversationally without calling `search_hotels` first!\n"
        "4. FORMAT HOTEL OPTIONS IN BOLD: Format hotel options as a numbered list with hotel names in **bold** (e.g., 1. **Hotel Name** - Price: $180/night) "
        "so the frontend can render option chips.\n"
        "5. STEP-BY-STEP BOOKING TURN SEQUENCE:\n"
        "   - Turn 1: If user wants to book a trip without destination, ask: 'Where would you like to travel?'\n"
        "   - Turn 2: Once destination is specified, invoke `search_hotels`. Present the list of hotels with bold names, and ask: 'To get started with your trip to [Destination], which hotel would you like to book?'\n"
        "   - Turn 3: Once hotel is selected, ask: 'What are your check-in and check-out dates?'\n"
        "   - Turn 4: If the destination is international (not in India), ask: 'What is your passport expiry date?' (Skip this check for domestic Indian destinations like Goa, Manali, Jaipur, Udaipur, Kerala, Rishikesh, Andaman, Lakshadweep, Ladakh, Darjeeling).\n"
        "   - Turn 5: Summarize the booking details (hotel, destination, dates) and ask: 'Please confirm if you want me to proceed with booking **[Hotel Name]** in **[Destination]** for **[Dates]**.'\n"
        "6. CANCELLATION FLOW: When the user asks to cancel a trip (e.g., 'Cancel my trip', 'Cancel booking', 'cancellation'), "
        "you MUST first call `get_user_trips` to retrieve and list their active bookings. You are STRICTLY FORBIDDEN from calling `cancel_booking` "
        "unless you already have the specific booking ID. Once you list the active bookings, ask the user to confirm which one they would like to cancel. "
        "Only call `cancel_booking` after the user confirms (e.g., says 'Yes', 'Confirm cancellation').\n"
        "7. WEATHER AND TRIP CONTEXT: If the user asks about weather, attractions, or details for an upcoming trip (e.g. 'weather during my bestie's trip', 'what is the weather in Rome'), "
        "first call `get_user_trips` to find their active trips, dates, and locations. Then call `get_weather` or `search_places` with the correct destination and dates retrieved. "
        "DO NOT make up or guess destinations or dates.\n"
        "8. DATE FORMAT CONVERSION: Always convert conversational date strings (e.g., '25th July to 30th July', 'Jul 25-30') to YYYY-MM-DD format (e.g., '2026-07-25') "
        "when passing them as arguments to your tools.\n"
        "9. NO PAYMENT HALLUCINATION: Do NOT mention payments, payment links, billing, or invoices. Journie does not handle payments inside this chat. Once the user confirms the booking, you MUST immediately call the `book_trip` tool to create the booking and provide the Booking ID. Never tell the user the booking is pending payment.\n\n"
        "Structure all responses in beautiful, premium standard Markdown. Use bolding (`**...**`) for key names, destinations, hotels, booking IDs, dates, and prices. Use italics (`*...*`) for side notes or warnings. Use clean bullet lists or numbered lists for formatting choices, trips, or instructions to make them extremely easy and aesthetic to read. Never use any emojis in your output."
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

    # 1. Capture user bookings status before chat run
    from app.services.booking_service import get_user_bookings
    bookings_before = await get_user_bookings(user_id=user_id, status="all")
    status_before = {b["id"]: b.get("status", "active") for b in bookings_before}

    # Run agent executor
    modified_flag = {"updated": False}
    reply_text = await run_agent_chat(
        system_prompt=system_content,
        user_message=request.message,
        chat_history=langchain_history,
        user_id=user_id,
        modified_flag=modified_flag
    )

    # 2. Capture user bookings status after chat run
    bookings_after = await get_user_bookings(user_id=user_id, status="all")
    status_after = {b["id"]: b.get("status", "active") for b in bookings_after}

    # 3. Determine if any booking was added or changed status (cancelled)
    booking_changed = False
    
    # Check for new bookings
    for b_id in status_after:
        if b_id not in status_before:
            booking_changed = True
            break
            
    # Check for status updates (e.g. active to cancelled)
    if not booking_changed:
        for b_id, stat_before in status_before.items():
            stat_after = status_after.get(b_id)
            if stat_after and stat_after != stat_before:
                booking_changed = True
                break

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

    booking_updated = booking_changed or modified_flag["updated"]

    return ChatResponse(reply=reply_text, booking_updated=booking_updated)