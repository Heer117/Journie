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

# WMO Weather Code Descriptions
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    95: "Thunderstorm"
}

from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from app.db import bookings_collection
import httpx
import os
import datetime



@tool
async def get_weather(destination: str, date: str) -> str:
    """
    Retrieves the weather forecast or historical weather for a given destination and date.
    Args:
        destination (str): The name of the city or location (e.g. Goa, Paris, Tokyo).
        date (str): The travel date in YYYY-MM-DD format.
    """
    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return f"Error: Date '{date}' must be in YYYY-MM-DD format."
        
    async with httpx.AsyncClient() as client:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={destination}&count=1&language=en&format=json"
        try:
            geo_res = await client.get(geo_url, timeout=8.0)
            if geo_res.status_code != 200:
                return f"Error: Could not search geocoding coordinates for '{destination}'."
            
            geo_data = geo_res.json()
            results = geo_data.get("results")
            if not results:
                return f"Error: Destination '{destination}' could not be resolved to coordinates."
            
            lat = results[0]["latitude"]
            lon = results[0]["longitude"]
            resolved_name = results[0].get("name", destination)
            country = results[0].get("country", "")
        except Exception as e:
            return f"Error resolving destination coordinates: {str(e)}"
            
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&start_date={date}&end_date={date}&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=auto"
        try:
            weather_res = await client.get(weather_url, timeout=8.0)
            if weather_res.status_code != 200:
                forecast_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=auto"
                weather_res = await client.get(forecast_url, timeout=8.0)
                if weather_res.status_code != 200:
                    return f"Error: Weather data not available for '{resolved_name}'."
                
                data = weather_res.json()
                daily = data.get("daily", {})
                times = daily.get("time", [])
                
                lines = [f"Note: Specific weather for date '{date}' is out of forecast range. Here is the current week's forecast for {resolved_name}, {country}:"]
                for t, tmin, tmax, code in zip(times, daily.get("temperature_2m_min", []), daily.get("temperature_2m_max", []), daily.get("weathercode", [])):
                    cond = WEATHER_CODES.get(code, "Clear")
                    lines.append(f"- {t}: Min: {tmin}°C, Max: {tmax}°C | {cond}")
                return "\n".join(lines)
                
            data = weather_res.json()
            daily = data.get("daily", {})
            if not daily or not daily.get("time"):
                return f"Weather data not found for date {date} at {resolved_name}."
            
            tmin = daily.get("temperature_2m_min", [None])[0]
            tmax = daily.get("temperature_2m_max", [None])[0]
            code = daily.get("weathercode", [None])[0]
            cond = WEATHER_CODES.get(code, "Clear")
            
            return f"Weather forecast for {resolved_name}, {country} on {date}: Min: {tmin}°C, Max: {tmax}°C | Condition: {cond}."
        except Exception as e:
            return f"Error retrieving weather data: {str(e)}"

@tool
async def search_places(query: str) -> str:
    """
    Searches for tourist attractions, itineraries, sights, restaurants, or things to do
    for a given destination or search query. Use this tool when the user asks for suggestions
    on what to do or see somewhere.
    Args:
        query (str): The search query (e.g. 'top attractions in Goa', 'things to do in Paris').
    """
    api_key = getattr(settings, "serpapi_api_key", None) or os.environ.get("SERPAPI_API_KEY")
    
    if api_key and api_key.strip():
        try:
            url = "https://serpapi.com/search.json"
            params = {
                "engine": "google",
                "q": query,
                "api_key": api_key
            }
            async with httpx.AsyncClient() as client:
                res = await client.get(url, params=params, timeout=10.0)
            if res.status_code == 200:
                data = res.json()
                results = []
                
                organic = data.get("organic_results", [])
                for item in organic[:5]:
                    title = item.get("title")
                    snippet = item.get("snippet")
                    link = item.get("link")
                    results.append(f"- **{title}**: {snippet} (Source: {link})")
                
                sights = data.get("top_sights", {}).get("sights", [])
                if sights:
                    results.append("\nTop Sights:")
                    for sight in sights[:5]:
                        name = sight.get("title")
                        desc = sight.get("description", "")
                        results.append(f"- **{name}**: {desc}")
                
                if results:
                    return "\n".join(results)
        except Exception as e:
            print(f"SerpAPI query failed: {e}")
            
    try:
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1
        }
        async with httpx.AsyncClient() as client:
            res = await client.get(url, params=params, timeout=8.0)
        if res.status_code == 200:
            data = res.json()
            abstract = data.get("AbstractText")
            related = data.get("RelatedTopics", [])
            results = []
            if abstract:
                results.append(abstract)
            
            topics = []
            for topic in related:
                if "Text" in topic:
                    topics.append(f"- {topic['Text']}")
                elif "Topics" in topic:
                    for sub in topic["Topics"]:
                        if "Text" in sub:
                            topics.append(f"- {sub['Text']}")
            
            if topics:
                results.append("Related Information:")
                results.extend(topics[:4])
            
            if results:
                return "\n".join(results)
    except Exception as e:
        print(f"DuckDuckGo search fallback failed: {e}")
        
    return f"Search recommendation (offline mode): Popular things to do for '{query}' include visiting scenic landmarks, trying local cuisine, and exploring historic city centers."

# Initialize tools list for global usage (excluding user trips which is instantiated dynamically per request)
tools = [get_weather, search_places]

# Setup dynamic prompt template for tool-calling agent
agent_prompt = ChatPromptTemplate.from_messages([
    ("system", "{system_prompt}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Create the agent and executor scaffold (global fallback)
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
                content = msg.get("data", {}).get("content", "")
                msg_type = msg.get("type")
                if msg_type == "human":
                    langchain_messages.append(HumanMessage(content=content))
                elif msg_type == "ai":
                    langchain_messages.append(AIMessage(content=content))
                elif msg_type == "system":
                    langchain_messages.append(SystemMessage(content=content))
        else:
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


async def run_agent_chat(system_prompt: str, user_message: str, chat_history: list[BaseMessage], user_id: str) -> str:
    from langchain_core.messages import ToolMessage

    @tool
    async def get_user_trips() -> str:
        """
        Retrieves all travel bookings, itineraries, and schedule details for the active user.
        Use this tool when the user asks about their own bookings, trip dates, or schedules.
        """
        try:
            cursor = bookings_collection.find({"user_id": user_id})
            bookings = await cursor.to_list(length=100)
            
            if not bookings:
                return "The user currently has no bookings recorded in the system."
            
            lines = []
            for b in bookings:
                relation = f" (for {b['booked_for']['name']} - {b['booked_for'].get('relation', 'Guest')})" if b.get("booked_for") else ""
                status = b.get("status", "active")
                doc_status = b.get("document_check", {}).get("status", "Pending")
                lines.append(
                    f"- Booking ID: {str(b['_id'])} | Destination: {b['destination']}{relation} | "
                    f"Hotel: {b['hotel_name']} | Dates: {b['start_date']} to {b['end_date']} | "
                    f"Status: {status} | Passport Expiry: {b['passport_expiry']} | Doc Check: {doc_status}"
                )
            return "\n".join(lines)
        except Exception as e:
            return f"Error retrieving trips: {str(e)}"

    local_tools = [get_user_trips, get_weather, search_places]
    tool_map = {t.name: t for t in local_tools}
    
    llm_with_tools = chat_model.bind_tools(local_tools)
    
    messages = [SystemMessage(content=system_prompt)]
    messages.extend(chat_history)
    messages.append(HumanMessage(content=user_message))
    
    try:
        res = await llm_with_tools.ainvoke(messages)
        
        max_tool_steps = 3
        step = 0
        while res.tool_calls and step < max_tool_steps:
            messages.append(res)
            for tool_call in res.tool_calls:
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("args", {})
                tool_id = tool_call.get("id")
                
                tool_func = tool_map.get(tool_name)
                if tool_func:
                    tool_output = await tool_func.ainvoke(tool_args)
                else:
                    tool_output = f"Tool '{tool_name}' not found."
                    
                messages.append(ToolMessage(content=str(tool_output), tool_call_id=tool_id))
            
            step += 1
            res = await llm_with_tools.ainvoke(messages)
            
        return res.content if res.content else "I'm here to help with your travel questions!"
    except Exception as e:
        print(f"[run_agent_chat error]: {e}")
        try:
            fallback_messages = [SystemMessage(content=system_prompt + "\nNote: Respond helpfully without emojis.")]
            fallback_messages.extend(chat_history)
            fallback_messages.append(HumanMessage(content=user_message))
            res = await chat_model.ainvoke(fallback_messages)
            return res.content
        except Exception as fallback_err:
            print(f"[fallback error]: {fallback_err}")
            return "I apologize, but I am currently having trouble retrieving that information. Please try again in a moment."
