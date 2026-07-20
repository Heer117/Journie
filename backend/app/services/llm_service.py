from langchain_groq import ChatGroq
from langchain_core.messages import (
    BaseMessage,
    SystemMessage,
    HumanMessage,
    AIMessage,
    message_to_dict,
    messages_from_dict,
)
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.config import settings

# Initialize ChatGroq model
chat_model = ChatGroq(
    model=settings.groq_model_name,
    api_key=settings.groq_api_key,
    temperature=0.7,
)

# Initialize empty tools list for Phase A (Phase B-E will append tools here)
tools = []

# Setup dynamic prompt template for tool-calling agent
agent_prompt = ChatPromptTemplate.from_messages([
    ("system", "{system_prompt}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Create the agent and executor scaffold
agent = create_tool_calling_agent(chat_model, tools, agent_prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


def get_chat_completion(messages: list[dict]) -> str:
    langchain_messages = []
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")
        if role == "system":
            langchain_messages.append(SystemMessage(content=content))
        elif role == "user":
            langchain_messages.append(HumanMessage(content=content))
        elif role == "assistant":
            langchain_messages.append(AIMessage(content=content))
        else:
            langchain_messages.append(HumanMessage(content=content))

    response = chat_model.invoke(langchain_messages)
    return response.content


def deserialize_messages(messages_list: list[dict]) -> list[BaseMessage]:
    langchain_messages = []
    for msg in messages_list:
        if "type" in msg and "data" in msg:
            try:
                langchain_messages.extend(messages_from_dict([msg]))
            except Exception:
                # Fallback to manual parsing if serialization layout is unexpected
                content = msg.get("data", {}).get("content", "")
                msg_type = msg.get("type")
                if msg_type == "human":
                    langchain_messages.append(HumanMessage(content=content))
                elif msg_type == "ai":
                    langchain_messages.append(AIMessage(content=content))
                elif msg_type == "system":
                    langchain_messages.append(SystemMessage(content=content))
        else:
            # Fallback for old {"role": "...", "content": "..."} format
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "system":
                langchain_messages.append(SystemMessage(content=content))
            elif role == "user":
                langchain_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))
            else:
                langchain_messages.append(HumanMessage(content=content))
    return langchain_messages


def run_agent_chat(system_prompt: str, user_message: str, chat_history: list[BaseMessage]) -> str:
    response = agent_executor.invoke({
        "system_prompt": system_prompt,
        "input": user_message,
        "chat_history": chat_history,
    })
    return response["output"]