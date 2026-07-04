from groq import Groq
from app.config import settings

_client = Groq(api_key=settings.groq_api_key)


def get_chat_completion(messages: list[dict]) -> str:
    response = _client.chat.completions.create(
        model=settings.groq_model,
        messages=messages,
        temperature=0.7,
    )
    return response.choices[0].message.content