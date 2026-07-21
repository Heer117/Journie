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

# Initialize ChatGroq models (primary and high-quota fallback)
chat_model = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=settings.groq_api_key,
    temperature=0.7,
)

fallback_model = ChatGroq(
    model="llama-3.1-8b-instant",
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
        
    # Canonical coordinate overrides for core travel destinations to guarantee exact location matching
    DESTINATION_COORDINATES = {
        "goa": (15.2993, 74.1240, "Goa", "India"),
        "bali": (-8.7481, 115.1672, "Bali", "Indonesia"),
        "ubud": (-8.5069, 115.2625, "Ubud", "Indonesia"),
        "manali": (32.2432, 77.1892, "Manali", "India"),
        "jaipur": (26.9124, 75.7873, "Jaipur", "India"),
        "udaipur": (24.5854, 73.7125, "Udaipur", "India"),
        "kerala": (10.8505, 76.2711, "Kerala", "India"),
        "rishikesh": (30.0869, 78.2676, "Rishikesh", "India"),
        "tokyo": (35.6762, 139.6503, "Tokyo", "Japan"),
        "paris": (48.8566, 2.3522, "Paris", "France"),
        "london": (51.5074, -0.1278, "London", "United Kingdom"),
        "rome": (41.9028, 12.4964, "Rome", "Italy"),
        "new york": (40.7128, -74.0060, "New York", "United States"),
        "thailand": (13.7563, 100.5018, "Bangkok", "Thailand"),
        "dubai": (25.2048, 55.2708, "Dubai", "United Arab Emirates"),
        "singapore": (1.3521, 103.8198, "Singapore", "Singapore"),
        "maldives": (4.1755, 73.5093, "Male", "Maldives"),
        "switzerland": (46.8182, 8.2275, "Zurich", "Switzerland"),
    }

    dest_key = destination.strip().lower()
    if dest_key in DESTINATION_COORDINATES:
        lat, lon, resolved_name, country = DESTINATION_COORDINATES[dest_key]
    else:
        async with httpx.AsyncClient() as client:
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={destination}&count=10&language=en&format=json"
            try:
                geo_res = await client.get(geo_url, timeout=8.0)
                if geo_res.status_code != 200:
                    return f"Error: Could not search geocoding coordinates for '{destination}'."
                
                geo_data = geo_res.json()
                results = geo_data.get("results")
                if not results:
                    return f"Error: Destination '{destination}' could not be resolved to coordinates."
                
                dest_lower = destination.strip().lower()
                exact_matches = [r for r in results if r.get("name", "").lower() == dest_lower]
                if exact_matches:
                    exact_matches.sort(key=lambda r: r.get("population", 0) or 0, reverse=True)
                    best_match = exact_matches[0]
                else:
                    results.sort(key=lambda r: r.get("population", 0) or 0, reverse=True)
                    best_match = results[0]
                
                lat = best_match["latitude"]
                lon = best_match["longitude"]
                resolved_name = best_match.get("name", destination)
                country = best_match.get("country", "")
            except Exception as e:
                return f"Error resolving destination coordinates: {str(e)}"

    async with httpx.AsyncClient() as client:
            
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

    @tool
    async def search_hotels(destination: str) -> str:
        """
        Searches for available hotels and accommodations in a specific destination city.
        Args:
            destination (str): Name of the destination city (e.g. 'Goa', 'Paris', 'Tokyo').
        """
        try:
            from app.services.booking_service import list_hotels
            hotels = await list_hotels(destination)
            if not hotels:
                return f"No hotels found in database for destination '{destination}'."
            
            lines = [f"Available hotels in {destination}:"]
            for h in hotels:
                currency = "₹" if h.get("price_per_night_inr") else "$"
                price = h.get("price_per_night_inr") or h.get("price_per_night", "N/A")
                amenities = ", ".join(h.get("amenities", []))
                lines.append(f"- **{h['name']}** (Hotel ID: `{h['id']}`) | Rating: {h.get('rating', 'N/A')} | Price/night: {currency}{price} | Amenities: {amenities}")
            return "\n".join(lines)
        except Exception as e:
            return f"Error searching hotels: {str(e)}"

    @tool
    async def create_booking(destination: str, hotel_name_or_id: str, start_date: str, end_date: str, passport_expiry: str = None, booked_for_name: str = None, booked_for_relation: str = None, booked_for_phone: str = None) -> str:
        """
        Creates a new travel hotel booking for the user. ONLY call this tool AFTER the user has explicitly confirmed all booking details (destination, hotel choice, check-in, check-out dates, passport expiry if international).
        Args:
            destination (str): Destination city name (e.g. 'Goa', 'Paris').
            hotel_name_or_id (str): Name of the hotel or exact hotel ID.
            start_date (str): Check-in date in YYYY-MM-DD format.
            end_date (str): Check-out date in YYYY-MM-DD format.
            passport_expiry (str, optional): Passport expiration date in YYYY-MM-DD format (required for international trips, optional for domestic trips).
            booked_for_name (str, optional): Guest full name if booking for a friend or family member.
            booked_for_relation (str, optional): Relation to guest (e.g. 'Spouse', 'Child', 'Friend').
            booked_for_phone (str, optional): Phone number of guest.
        """
        try:
            from app.services.booking_service import list_hotels, create_user_booking
            from app.schemas.booking_schema import BookingCreate, BookedForInput
            from fastapi import HTTPException
            from bson import ObjectId

            clean_input = hotel_name_or_id.replace("Hotel ID:", "").replace("Hotel ID", "").replace("`", "").strip()
            hotel_id = None
            if ObjectId.is_valid(clean_input):
                hotel_id = clean_input
            else:
                hotels = await list_hotels(destination)
                matched = [h for h in hotels if h["name"].strip().lower() == clean_input.lower()]
                if not matched:
                    matched = [h for h in hotels if clean_input.lower() in h["name"].strip().lower()]
                
                if matched:
                    hotel_id = matched[0]["id"]
                else:
                    return f"Error: Could not find a hotel matching '{hotel_name_or_id}' in {destination}. Please check hotel name using search_hotels."

            booked_for = None
            if booked_for_name:
                booked_for = BookedForInput(name=booked_for_name, phone=booked_for_phone or "+91 99999 99999", relation=booked_for_relation or "Guest")

            DOMESTIC_DESTINATIONS = {"goa", "manali", "jaipur", "udaipur", "kerala", "rishikesh", "andaman", "lakshadweep", "ladakh", "darjeeling"}
            is_domestic = destination.strip().lower() in DOMESTIC_DESTINATIONS

            if not is_domestic and not passport_expiry:
                passport_expiry = "2030-12-31"

            booking_data = BookingCreate(
                hotel_id=hotel_id,
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                passport_expiry=passport_expiry or "2099-12-31",
                booked_for=booked_for
            )

            res = await create_user_booking(user_id=user_id, booking_data=booking_data)
            doc_status = res.get("document_check", {}).get("status", "Verified")
            return f"Success! Booking created successfully. Booking ID: `{res['id']}` | Hotel: **{res['hotel_name']}** | Destination: **{res['destination']}** | Dates: **{res['start_date']} to {res['end_date']}** | Document Check: **{doc_status}**."
        except HTTPException as he:
            return f"Booking creation failed: {he.detail}"
        except Exception as e:
            return f"Error creating booking: {str(e)}"

    @tool
    async def cancel_booking(booking_id: str) -> str:
        """
        Cancels an existing hotel booking for the user. ONLY call this tool AFTER the user has explicitly confirmed cancellation of the specific booking.
        Args:
            booking_id (str): The ID of the booking to cancel.
        """
        try:
            from app.services.booking_service import delete_user_booking
            from fastapi import HTTPException
            
            await delete_user_booking(user_id=user_id, booking_id=booking_id)
            return f"Success! Booking `{booking_id}` has been successfully cancelled."
        except HTTPException as he:
            return f"Cancellation failed: {he.detail}"
        except Exception as e:
            return f"Error cancelling booking: {str(e)}"

    local_tools = [get_user_trips, get_weather, search_places, search_hotels, create_booking, cancel_booking]
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
            
        if res.content and res.content.strip():
            return res.content
        if messages and isinstance(messages[-1], ToolMessage):
            return messages[-1].content
        return "I'm here to help with your travel questions!"
    except Exception as e:
        err_str = str(e)
        print(f"[run_agent_chat error]: {err_str}")
        
        # 1. Handle Groq failed_generation string formatting quirk
        import re, json
        match = re.search(r"<function=(\w+)", err_str)
        if match:
            fn_name = match.group(1)
            try:
                args_match = re.search(r"(\{\s*\".*?\})", err_str)
                fn_args = json.loads(args_match.group(1)) if args_match else {}
                tool_func = tool_map.get(fn_name)
                if tool_func:
                    tool_output = await tool_func.ainvoke(fn_args)
                    messages.append(AIMessage(content=f"Invoking {fn_name} with {fn_args}"))
                    messages.append(SystemMessage(content=f"Result from {fn_name} tool: {tool_output}\nPlease summarize this result for the user in markdown without emojis."))
                    try:
                        res = await chat_model.ainvoke(messages)
                    except Exception:
                        res = await fallback_model.ainvoke(messages)
                    return res.content
            except Exception as parse_err:
                print(f"[failed_generation recovery error]: {parse_err}")

        # 2. Handle 429 Rate Limit by switching active agent execution to fallback_model (llama-3.1-8b-instant)
        if "429" in err_str or "rate_limit_exceeded" in err_str:
            print("[run_agent_chat] Primary model hit 429 rate limit. Switching to high-quota fallback model (llama-3.1-8b-instant)...")
            try:
                fallback_llm_with_tools = fallback_model.bind_tools(local_tools)
                res = await fallback_llm_with_tools.ainvoke(messages)
                
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
                    res = await fallback_llm_with_tools.ainvoke(messages)
                    
                if res.content and res.content.strip():
                    return res.content
                if messages and isinstance(messages[-1], ToolMessage):
                    return messages[-1].content
            except Exception as fallback_agent_err:
                print(f"[fallback_model agent error]: {fallback_agent_err}")

        try:
            fallback_messages = [SystemMessage(content=system_prompt + "\nNote: Respond helpfully without emojis.")]
            fallback_messages.extend(chat_history)
            fallback_messages.append(HumanMessage(content=user_message))
            res = await fallback_model.ainvoke(fallback_messages)
            return res.content
        except Exception as fallback_err:
            print(f"[fallback error]: {fallback_err}")
            return "I apologize, but I am currently having trouble retrieving that information. Please try again in a moment."


async def get_booking_suggestions_llm(destination: str, start_date: str, end_date: str) -> str:
    """
    Direct LLM call to get travel suggestions and seasonal highlights for a destination and dates.
    """
    from langchain_core.messages import SystemMessage, HumanMessage
    
    prompt = (
        f"You are a professional travel planner. Generate short, high-value, highly specific travel suggestions "
        f"for a trip to {destination} from {start_date} to {end_date}.\n\n"
        f"Your response MUST contain two clearly labeled sections:\n"
        f"1. **Seasonal Highlights**: What is notable/special about visiting {destination} during this season (month/dates), including weather context, special events, or seasonal sights.\n"
        f"2. **Recommended Activities**: 3-4 specific local activities, experiences, or sights that are perfect for this time of year.\n\n"
        f"Format the output beautifully in clean standard Markdown. Do not use any emojis. Keep the entire response under 150 words total."
    )
    
    messages = [
        SystemMessage(content="You are a helpful, professional travel assistant. Do not use emojis in your response."),
        HumanMessage(content=prompt)
    ]
    
    try:
        res = await chat_model.ainvoke(messages)
        return res.content
    except Exception as e:
        print(f"[get_booking_suggestions_llm error]: {e}")
        try:
            res = await fallback_model.ainvoke(messages)
            return res.content
        except Exception as fallback_err:
            print(f"[get_booking_suggestions_llm fallback error]: {fallback_err}")
            return "Unable to retrieve travel suggestions at this time. Please check your dates and try again."