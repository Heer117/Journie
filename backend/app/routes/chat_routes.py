from fastapi import APIRouter, Depends
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.llm_service import get_chat_completion
from app.db import conversations_collection
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

    reply_text = get_chat_completion(history)

    history.append({"role": "assistant", "content": reply_text})

    await conversations_collection.update_one(
        {"user_id": user_id},
        {"$set": {"messages": history}},
        upsert=True,
    )

    return ChatResponse(reply=reply_text)