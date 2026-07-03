from fastapi import APIRouter
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.llm_service import get_chat_completion
from app.db import conversations_collection

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Single chat turn:
    1. Load this user's past conversation history from Mongo
    2. Append their new message
    3. Send the full history to Groq
    4. Save the updated history back to Mongo
    5. Return the assistant's reply
    """
    conversation = await conversations_collection.find_one({"user_id": request.user_id})

    if conversation is None:
        history = []
    else:
        history = conversation["messages"]

    history.append({"role": "user", "content": request.message})

    reply_text = get_chat_completion(history)

    history.append({"role": "assistant", "content": reply_text})

    await conversations_collection.update_one(
        {"user_id": request.user_id},
        {"$set": {"messages": history}},
        upsert=True,
    )

    return ChatResponse(reply=reply_text)