import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from app.config import settings
from app.services.llm_service import get_weather, search_places

chat_model = ChatGroq(
    model=settings.groq_model_name,
    api_key=settings.groq_api_key,
    temperature=0.7,
)

async def main():
    print("--- Testing bind_tools with ChatGroq ---")
    
    tools = [get_weather, search_places]
    tool_map = {t.name: t for t in tools}
    
    llm_with_tools = chat_model.bind_tools(tools)
    
    messages = [
        SystemMessage(content="You are Journie, a helpful travel assistant. NEVER use emojis."),
        HumanMessage(content="What is the weather forecast for Udaipur on 2026-07-23?")
    ]
    
    res = await llm_with_tools.ainvoke(messages)
    print("Initial LLM Response:", res)
    print("Tool calls:", res.tool_calls)
    
    if res.tool_calls:
        messages.append(res)
        for tool_call in res.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            print(f"Executing tool {tool_name} with args {tool_args}...")
            tool_func = tool_map[tool_name]
            tool_output = await tool_func.ainvoke(tool_args)
            print("Tool output:", tool_output)
            messages.append(ToolMessage(content=str(tool_output), tool_call_id=tool_call["id"]))
        
        final_res = await llm_with_tools.ainvoke(messages)
        print("\nFinal Response from LLM:\n", final_res.content)

if __name__ == "__main__":
    asyncio.run(main())
