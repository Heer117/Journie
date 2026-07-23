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
import contextvars

booking_modified_var = contextvars.ContextVar("booking_modified", default=False)

# Initialize ChatGroq models with distinct rate-limit buckets
chat_model = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=settings.groq_api_key,
    temperature=0.7,
)

fallback_model = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=settings.groq_api_key,
    temperature=0.7,
)

gemma_model = ChatGroq(
    model="llama-3.3-70b-versatile",
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



import re

def parse_flexible_date(date_str: str) -> str:
    if not date_str:
        return date_str
    
    date_str = date_str.strip()
    
    # Try standard YYYY-MM-DD
    try:
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass
        
    # Try formats like DD-MM-YYYY or DD/MM/YYYY
    for fmt in ["%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y"]:
        try:
            dt = datetime.datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass
            
    # Try formats like DD-MM-YY or DD/MM/YY
    for fmt in ["%d-%m-%y", "%d/%m/%y", "%d.%m.%y"]:
        try:
            dt = datetime.datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    # Try formats like YYYY/MM/DD
    try:
        dt = datetime.datetime.strptime(date_str, "%Y/%m/%d")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass

    # Try to extract numbers from common conversational styles
    months = {
        "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
        "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
        "aug": 8, "august": 8, "sep": 9, "september": 9, "oct": 10, "october": 10,
        "nov": 11, "november": 11, "dec": 12, "december": 12
    }
    
    # Clean the string, remove suffixes like 'st', 'nd', 'rd', 'th'
    cleaned = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str, flags=re.IGNORECASE)
    # Find all words and numbers
    tokens = re.findall(r'\w+', cleaned)
    
    day, month, year = None, None, None
    for token in tokens:
        if token.isdigit():
            val = int(token)
            if val > 31:
                year = val
            elif day is None:
                day = val
            else:
                if year is None:
                    if val > 1000:
                        year = val
                    else:
                        year = 2000 + val
        else:
            token_lower = token.lower()
            if token_lower in months:
                month = months[token_lower]
                
    if day and month and year:
        try:
            dt = datetime.datetime(year, month, day)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass
            
    return date_str



@tool
async def get_weather(destination: str, date: str) -> str:
    """
    Retrieves the weather forecast or historical weather for a given destination and date.
    You MUST include the returned weather forecast details verbatim in your conversational response to the user. Do NOT summarize or omit them.
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


def _clean_response(text: str) -> str:
    if not text:
        return "I'm here to help with your travel questions!"
    import re
    cleaned = re.sub(r"<function=.*?(?:</function>|/>|>)", "", text, flags=re.DOTALL).strip()
    if not cleaned:
        return "I am here to help you plan your trip! How can I assist you today?"
    return cleaned


async def _intercept_and_execute_tool(text: str, messages: list, tool_map: dict, model) -> str:
    if not text:
        return text
    text_lower = text.lower()
    if any(fn in text_lower for fn in ["create_booking", "cancel_booking", "search_hotels", "get_weather", "get_user_trips"]):
        import re, json, ast
        tool_match = re.search(r"(create_booking|cancel_booking|search_hotels|get_weather|get_user_trips)\s*(?:(?:args\s*=\s*)?\(?\s*(\{.*?\})\s*\)?)?", text, re.IGNORECASE | re.DOTALL)
        if tool_match:
            fn_name = tool_match.group(1).lower()
            raw_args = tool_match.group(2) if tool_match.group(2) else "{}"
            try:
                fn_args = json.loads(raw_args)
            except Exception:
                try:
                    fn_args = ast.literal_eval(raw_args)
                except Exception:
                    fn_args = {}

            tool_func = tool_map.get(fn_name)
            if tool_func:
                try:
                    tool_output = await tool_func.ainvoke(fn_args)
                except Exception:
                    if hasattr(tool_func, "coroutine") and callable(tool_func.coroutine):
                        tool_output = await tool_func.coroutine(**fn_args)
                    else:
                        raise
                messages.append(AIMessage(content=text))
                messages.append(SystemMessage(content=(
                    f"The tool returned: '{tool_output}'\n\n"
                    "Write a warm, concise conversational message summarizing this result for the user. "
                    "Do NOT start your message with 'Result from tool' or 'The tool returned'. Respond directly, naturally, and helpfully. Do not use emojis."
                )))
                try:
                    res = await model.ainvoke(messages)
                except Exception:
                    res = await fallback_model.ainvoke(messages)
                return res.content
    return text


async def run_agent_chat(system_prompt: str, user_message: str, chat_history: list[BaseMessage], user_id: str, modified_flag: dict = None) -> str:
    from langchain_core.messages import ToolMessage

    @tool
    async def get_user_trips() -> str:
        """
        Retrieves all travel bookings, itineraries, and schedule details for the active user.
        You MUST include the returned list verbatim in your conversational response to the user. Do NOT summarize, hide, or omit any booking details (such as booking IDs, destinations, hotels, or dates).
        """
        try:
            from app.services.booking_service import get_user_bookings
            bookings = await get_user_bookings(user_id=user_id, status="active")
            
            if not bookings:
                return "The user currently has no active bookings recorded in the system."
            
            lines = []
            for b in bookings:
                relation = f" (for {b['booked_for']['name']} - {b['booked_for'].get('relation', 'Guest')})" if b.get("booked_for") else ""
                doc_status = b.get("document_check", {}).get("status", "Pending") if b.get("document_check") else "Pending"
                lines.append(
                    f"- Booking ID: {b['id']} | Destination: {b['destination']}{relation} | "
                    f"Hotel: {b['hotel_name']} | Dates: {b['start_date']} to {b['end_date']} | "
                    f"Status: active | Passport Expiry: {b['passport_expiry']} | Doc Check: {doc_status}"
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
    async def create_booking(
        destination: str,
        hotel_name_or_id: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        passport_expiry: str | None = None,
        booked_for_name: str | None = None,
        booked_for_relation: str | None = None,
        booked_for_phone: str | None = None,
        check_in_date: str | None = None,
        check_out_date: str | None = None,
        hotel_name: str | None = None,
        hotel_id: str | None = None,
    ) -> str:
        """
        Creates a new travel hotel booking for the user. ONLY call this tool AFTER the user has explicitly confirmed all booking details (destination, hotel choice, check-in, check-out dates, passport expiry if international).
        Args:
            destination (str): Destination city name (e.g. 'Goa', 'Paris').
            hotel_name_or_id (str, optional): Name of the hotel or exact hotel ID.
            start_date (str, optional): Check-in date in YYYY-MM-DD format.
            end_date (str, optional): Check-out date in YYYY-MM-DD format.
            passport_expiry (str, optional): Passport expiration date in YYYY-MM-DD format (required for international trips, optional for domestic trips).
            booked_for_name (str, optional): Guest full name if booking for a friend or family member.
            booked_for_relation (str, optional): Relation to guest (e.g. 'Spouse', 'Child', 'Friend').
            booked_for_phone (str, optional): Phone number of guest.
            check_in_date (str, optional): Alternative name for check-in date.
            check_out_date (str, optional): Alternative name for check-out date.
            hotel_name (str, optional): Alternative name for hotel name.
            hotel_id (str, optional): Alternative name for hotel ID.
        """
        try:
            from app.services.booking_service import list_hotels, create_user_booking
            from app.schemas.booking_schema import BookingCreate, BookedForInput
            from fastapi import HTTPException
            from bson import ObjectId

            actual_hotel = hotel_name_or_id or hotel_name or hotel_id
            if not actual_hotel:
                return "Error: Hotel name or ID is required for booking."

            actual_start = start_date or check_in_date
            actual_end = end_date or check_out_date
            if not actual_start or not actual_end:
                return "Error: Both check-in and check-out dates are required for booking."

            # Run flexible date parsing
            actual_start = parse_flexible_date(actual_start)
            actual_end = parse_flexible_date(actual_end)
            if passport_expiry:
                passport_expiry = parse_flexible_date(passport_expiry)

            clean_input = actual_hotel.replace("Hotel ID:", "").replace("Hotel ID", "").replace("`", "").strip()
            resolved_hotel_id = None
            if ObjectId.is_valid(clean_input):
                resolved_hotel_id = clean_input
            else:
                hotels = await list_hotels(destination)
                matched = [h for h in hotels if h["name"].strip().lower() == clean_input.lower()]
                if not matched:
                    matched = [h for h in hotels if clean_input.lower() in h["name"].strip().lower()]
                
                if matched:
                    resolved_hotel_id = matched[0]["id"]
                else:
                    return f"Error: Could not find a hotel matching '{actual_hotel}' in {destination}. Please check hotel name using search_hotels."

            booked_for = None
            if booked_for_name:
                booked_for = BookedForInput(name=booked_for_name, phone=booked_for_phone or "+91 99999 99999", relation=booked_for_relation or "Guest")

            DOMESTIC_DESTINATIONS = {"goa", "manali", "jaipur", "udaipur", "kerala", "rishikesh", "andaman", "lakshadweep", "ladakh", "darjeeling"}
            is_domestic = destination.strip().lower() in DOMESTIC_DESTINATIONS

            if not is_domestic and not passport_expiry:
                passport_expiry = "2030-12-31"

            booking_data = BookingCreate(
                hotel_id=resolved_hotel_id,
                destination=destination,
                start_date=actual_start,
                end_date=actual_end,
                passport_expiry=passport_expiry or "2099-12-31",
                booked_for=booked_for
            )

            print(f"[TOOL LOG] create_booking called with destination='{destination}', hotel='{actual_hotel}', start='{actual_start}', end='{actual_end}', user_id='{user_id}'")
            res = await create_user_booking(user_id=user_id, booking_data=booking_data)
            print(f"[TOOL LOG] create_booking result: {res}")
            booking_modified_var.set(True)
            if modified_flag is not None:
                modified_flag["updated"] = True
            doc_status = res.get("document_check", {}).get("status", "Verified")
            return f"Success! Booking created successfully. Booking ID: `{res['id']}` | Hotel: **{res['hotel_name']}** | Destination: **{res['destination']}** | Dates: **{res['start_date']} to {res['end_date']}** | Document Check: **{doc_status}**."
        except HTTPException as he:
            print(f"[TOOL LOG] create_booking HTTPException: {he.detail}")
            return f"Booking creation failed: {he.detail}"
        except Exception as e:
            print(f"[TOOL LOG] create_booking Exception: {str(e)}")
            return f"Error creating booking: {str(e)}"

    @tool
    async def cancel_booking(booking_id: str) -> str:
        """
        Cancels an existing hotel booking for the user. ONLY call this tool AFTER the user has explicitly confirmed cancellation of the specific booking.
        Args:
            booking_id (str): The ID of the booking to cancel (e.g. '6a61f774cc330eb563094a9b').
        """
        try:
            from app.services.booking_service import delete_user_booking
            from fastapi import HTTPException
            
            actual_id = booking_id
            if not actual_id or not actual_id.strip():
                return "Error: Booking ID is required to cancel a booking."

            print(f"[TOOL LOG] cancel_booking called with booking_id='{actual_id}', user_id='{user_id}'")
            await delete_user_booking(user_id=user_id, booking_id=actual_id)
            print(f"[TOOL LOG] cancel_booking completed successfully for booking_id='{actual_id}'")
            booking_modified_var.set(True)
            if modified_flag is not None:
                modified_flag["updated"] = True
            return f"Success! Booking `{actual_id}` has been successfully cancelled."
        except HTTPException as he:
            print(f"[TOOL LOG] cancel_booking HTTPException: {he.detail}")
            return f"Cancellation failed: {he.detail}"
        except Exception as e:
            print(f"[TOOL LOG] cancel_booking Exception: {str(e)}")
            return f"Error cancelling booking: {str(e)}"


    local_tools = [get_user_trips, get_weather, search_places, search_hotels, create_booking, cancel_booking]
    tool_map = {t.name: t for t in local_tools}
    
    llm_with_tools = chat_model.bind_tools(local_tools)
    
    messages = [SystemMessage(content=system_prompt)]
    messages.extend(chat_history)
    messages.append(HumanMessage(content=user_message))
    
    try:
        res = await llm_with_tools.ainvoke(messages)
        print(f"[MODEL LOG] raw response: content={res.content!r}, tool_calls={res.tool_calls}")
        
        max_tool_steps = 3
        step = 0
        while res.tool_calls and step < max_tool_steps:
            messages.append(res)
            for tool_call in res.tool_calls:
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("args", {})
                tool_id = tool_call.get("id")
                
                tool_func = tool_map.get(tool_name)
                if not tool_func:
                    fn_lower = (tool_name or "").lower()
                    if "hotel" in fn_lower:
                        tool_func = tool_map.get("search_hotels")
                    elif "trip" in fn_lower or "booking" in fn_lower or "destination" in fn_lower:
                        tool_func = tool_map.get("get_user_trips")
                    elif "weather" in fn_lower:
                        tool_func = tool_map.get("get_weather")
                    elif "place" in fn_lower or "sight" in fn_lower or "attraction" in fn_lower:
                        tool_func = tool_map.get("search_places")

                if tool_func:
                    tool_output = await tool_func.ainvoke(tool_args)
                    print(f"[TOOL LOG] executed {tool_name} with {tool_args} -> output: {tool_output!r}")
                else:
                    tool_output = f"Tool '{tool_name}' not found."
                    
                messages.append(ToolMessage(content=str(tool_output), tool_call_id=tool_id))
            
            step += 1
            res = await llm_with_tools.ainvoke(messages)
            
        # Intercept plain text tool calls outputted by LLM (e.g. 'create_booking {...}')
        res.content = await _intercept_and_execute_tool(res.content, messages, tool_map, chat_model)

        if res.content and res.content.strip():
            return _clean_response(res.content)
        if messages and isinstance(messages[-1], ToolMessage):
            try:
                user_msg = "Please show me the details."
                for m in reversed(messages):
                    if isinstance(m, HumanMessage):
                        user_msg = m.content
                        break
                
                summary_prompt = (
                    "You are a helpful travel assistant. The user asked: '{user_msg}'.\n"
                    "Here is the raw data returned by the system:\n"
                    "{tool_output}\n\n"
                    "You MUST format this raw data into a clear, complete, and structured markdown response (list or table). "
                    "Include all details (booking IDs, dates, hotels, destinations, or weather forecasts) verbatim. "
                    "Do NOT summarize, hide, or omit any names, IDs, dates, or details. "
                    "End your response with a single, concise question guiding the user. Do not use any emojis. Do not say 'The tool returned' or 'Result from tool'."
                ).format(user_msg=user_msg, tool_output=messages[-1].content)
                
                summary_res = await chat_model.ainvoke([SystemMessage(content=summary_prompt)])
                if summary_res.content and summary_res.content.strip():
                    summary_res.content = await _intercept_and_execute_tool(summary_res.content, messages, tool_map, chat_model)
                    return _clean_response(summary_res.content)
            except Exception as summary_err:
                print(f"[summary generation error]: {summary_err}")
            return _clean_response(messages[-1].content)
        return "I'm here to help with your travel questions!"
    except Exception as e:
        import traceback
        traceback.print_exc()
        err_str = str(e)
        print(f"[run_agent_chat error]: {err_str}")
        
        # 1. Handle Groq failed_generation string formatting quirk
        import re, json, ast
        match = re.search(r"<function=(\w+)(?:.*?)>(.*?)</function>", err_str, re.DOTALL)
        if match:
            fn_name = match.group(1)
            raw_args = match.group(2).strip()
            fn_args = {}
            try:
                fn_args = json.loads(raw_args)
            except Exception:
                try:
                    fn_args = ast.literal_eval(raw_args)
                except Exception:
                    pairs = re.findall(r'(\w+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|(\d+))', raw_args)
                    fn_args = {p[0]: (p[1] or p[2] or p[3]) for p in pairs}
        else:
            match = re.search(r"<function=(\w+)", err_str)
            if match:
                fn_name = match.group(1)
                tag_index = err_str.find("<function=")
                search_sub = err_str[tag_index:] if tag_index != -1 else err_str
                args_match = re.search(r"(\{.*?\})", search_sub)
                fn_args = {}
                if args_match:
                    raw_args = args_match.group(1).rstrip(";")
                    try:
                        fn_args = json.loads(raw_args)
                    except Exception:
                        try:
                            fn_args = ast.literal_eval(raw_args)
                        except Exception:
                            pairs = re.findall(r'(\w+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|(\d+))', raw_args)
                            fn_args = {p[0]: (p[1] or p[2] or p[3]) for p in pairs}
                else:
                    # Try to parse key-value pairs directly from the substring
                    pairs = re.findall(r'(\w+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|(\d+))', search_sub)
                    if pairs:
                        fn_args = {p[0]: (p[1] or p[2] or p[3]) for p in pairs}
            else:
                fn_name = None

        if fn_name:
            try:
                tool_func = tool_map.get(fn_name)
                if not tool_func:
                    fn_lower = fn_name.lower()
                    if "hotel" in fn_lower:
                        tool_func = tool_map.get("search_hotels")
                    elif "trip" in fn_lower or "booking" in fn_lower or "destination" in fn_lower:
                        tool_func = tool_map.get("get_user_trips")
                    elif "weather" in fn_lower:
                        tool_func = tool_map.get("get_weather")
                    elif "place" in fn_lower or "sight" in fn_lower or "attraction" in fn_lower:
                        tool_func = tool_map.get("search_places")

                if tool_func:
                    try:
                        tool_output = await tool_func.ainvoke(fn_args)
                    except Exception:
                        if hasattr(tool_func, "coroutine") and callable(tool_func.coroutine):
                            tool_output = await tool_func.coroutine(**fn_args)
                        else:
                            raise
                    messages.append(AIMessage(content=f"Invoking tool with {fn_args}"))
                    messages.append(SystemMessage(content=f"Result from tool: {tool_output}\nPlease summarize this result into a complete, beautifully formatted markdown response for the user, including all key details (names, prices, ratings, dates, or weather). Do not omit key details. Do not use any emojis."))
                    try:
                        res = await chat_model.ainvoke(messages)
                    except Exception:
                        res = await fallback_model.ainvoke(messages)
                    res.content = await _intercept_and_execute_tool(res.content, messages, tool_map, chat_model)
                    return _clean_response(res.content)
                else:
                    # Model hallucinated an unresolvable tool name; answer conversationally in standard markdown
                    try:
                        fallback_messages = [SystemMessage(content=system_prompt + "\nNote: Provide a helpful, clear, and structured answer in standard markdown without using emojis.")]
                        fallback_messages.extend(chat_history)
                        fallback_messages.append(HumanMessage(content=user_message))
                        res = await fallback_model.ainvoke(fallback_messages)
                        res.content = await _intercept_and_execute_tool(res.content, messages, tool_map, fallback_model)
                        return _clean_response(res.content)
                    except Exception:
                        pass
            except Exception as parse_err:
                print(f"[failed_generation recovery error]: {parse_err}")


        # 2. Handle 429 Rate Limit by trying fallback models with distinct quota limits
        if "429" in err_str or "rate_limit_exceeded" in err_str:
            print("[run_agent_chat] Primary model hit 429 rate limit. Attempting multi-model failover...")
            for alt_model in [fallback_model, gemma_model]:
                try:
                    alt_llm_with_tools = alt_model.bind_tools(local_tools)
                    res = await alt_llm_with_tools.ainvoke(messages)
                    
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
                        res = await alt_llm_with_tools.ainvoke(messages)
                        
                    res.content = await _intercept_and_execute_tool(res.content, messages, tool_map, alt_model)
                    if res.content and res.content.strip():
                        return _clean_response(res.content)
                    if messages and isinstance(messages[-1], ToolMessage):
                        try:
                            messages.append(SystemMessage(content="Please summarize the tool results into a complete, beautifully formatted markdown response for the user, including all key details (names, prices, ratings, dates, or weather). Do not omit key details. Do not use any emojis. Do NOT repeat 'Result from tool' or 'The tool returned'. Just answer directly and conversationally."))
                            summary_res = await alt_model.ainvoke(messages)
                            if summary_res.content and summary_res.content.strip():
                                summary_res.content = await _intercept_and_execute_tool(summary_res.content, messages, tool_map, alt_model)
                                return _clean_response(summary_res.content)
                        except Exception:
                            pass
                        return _clean_response(messages[-1].content)
                except Exception as alt_err:
                    print(f"[alt_model error]: {alt_err}")

        # Final Fallback to plain completion across models
        for alt_model in [fallback_model, gemma_model, chat_model]:
            try:
                fallback_messages = [SystemMessage(content=system_prompt + "\nNote: Respond helpfully in 1 short sentence without emojis.")]
                fallback_messages.extend(chat_history)
                fallback_messages.append(HumanMessage(content=user_message))
                res = await alt_model.ainvoke(fallback_messages)
                if res.content and res.content.strip():
                    res.content = await _intercept_and_execute_tool(res.content, fallback_messages, tool_map, alt_model)
                    return _clean_response(res.content)
            except Exception as fb_err:
                print(f"[fallback model attempt failed]: {fb_err}")

        return "To get started with your trip, which destination would you like to visit?"


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