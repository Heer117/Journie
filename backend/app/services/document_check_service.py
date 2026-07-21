import datetime
from bson import ObjectId
from fastapi import HTTPException, status
from app.db import document_checks_collection
from app.services.llm_service import get_chat_completion

# Lookup table mapping destinations (cities or countries) to country names,
# passport validity requirements (days beyond return date), and visa rules.
PASSPORT_VALIDITY_MAP = {
    "tokyo": {"country": "Japan", "days": 90, "visa": "Visa-free for tourist stays up to 90 days."},
    "paris": {"country": "France", "days": 90, "visa": "Schengen visa-exempt for tourist stays up to 90 days."},
    "london": {"country": "United Kingdom", "days": 90, "visa": "Visa-free for tourist stays up to 6 months for most visitors."},
    "rome": {"country": "Italy", "days": 90, "visa": "Schengen visa-exempt for tourist stays up to 90 days."},
    "new york": {"country": "United States", "days": 180, "visa": "ESTA or tourist visa required for international travelers."},
    
    # Countries
    "japan": {"country": "Japan", "days": 90, "visa": "Visa-free for tourist stays up to 90 days."},
    "france": {"country": "France", "days": 90, "visa": "Schengen visa-exempt for tourist stays up to 90 days."},
    "united kingdom": {"country": "United Kingdom", "days": 90, "visa": "Visa-free for tourist stays up to 6 months."},
    "italy": {"country": "Italy", "days": 90, "visa": "Schengen visa-exempt for tourist stays up to 90 days."},
    "united states": {"country": "United States", "days": 180, "visa": "ESTA or tourist visa required for international travelers."},
    "canada": {"country": "Canada", "days": 180, "visa": "eTA or tourist visa required for most international visitors."},
    "australia": {"country": "Australia", "days": 180, "visa": "eVisitor or tourist visa required before arrival."},
    "india": {"country": "India", "days": 180, "visa": "e-Visa or regular tourist visa required before travel."},
    "singapore": {"country": "Singapore", "days": 180, "visa": "SG Arrival Card and tourist visa-exempt up to 30 days for most."},
    "thailand": {"country": "Thailand", "days": 180, "visa": "Visa-exempt for tourist stays up to 30 or 60 days for many countries."},
    "united arab emirates": {"country": "United Arab Emirates", "days": 180, "visa": "Visa on arrival or pre-arranged tourist visa depending on nationality."},
    "switzerland": {"country": "Switzerland", "days": 90, "visa": "Schengen visa-exempt for tourist stays up to 90 days."},
    "netherlands": {"country": "Netherlands", "days": 90, "visa": "Schengen visa-exempt for tourist stays up to 90 days."},
    "germany": {"country": "Germany", "days": 90, "visa": "Schengen visa-exempt for tourist stays up to 90 days."},
    "spain": {"country": "Spain", "days": 90, "visa": "Schengen visa-exempt for tourist stays up to 90 days."},
    
    # Expanded international destinations
    "dubai": {"country": "United Arab Emirates", "days": 180, "visa": "Visa on arrival or pre-arranged tourist visa depending on nationality."},
    "bali": {"country": "Indonesia", "days": 180, "visa": "Visa on Arrival (VoA) required for tourist stays up to 30 days."},
    "indonesia": {"country": "Indonesia", "days": 180, "visa": "Visa on Arrival (VoA) required for tourist stays up to 30 days."},
    "maldives": {"country": "Maldives", "days": 180, "visa": "Free 30-day visa on arrival for all nationalities."},
    "vietnam": {"country": "Vietnam", "days": 180, "visa": "e-Visa or tourist visa required before travel."},
    "sri lanka": {"country": "Sri Lanka", "days": 180, "visa": "ETA or tourist visa required before arrival."},
    "south korea": {"country": "South Korea", "days": 180, "visa": "K-ETA or tourist visa required."},
    "korea": {"country": "South Korea", "days": 180, "visa": "K-ETA or tourist visa required."},
    "turkey": {"country": "Turkey", "days": 180, "visa": "e-Visa or sticker visa required before arrival."}
}

async def perform_document_check(
    user_id: str,
    booking_id: str,
    destination: str,
    end_date_str: str,
    passport_expiry_str: str
) -> dict:
    dest_key = destination.strip().lower()
    
    # Skip checks entirely for domestic destinations
    DOMESTIC_DESTINATIONS = {"goa", "manali", "jaipur", "udaipur", "kerala", "rishikesh", "andaman", "lakshadweep", "ladakh", "darjeeling"}
    if dest_key in DOMESTIC_DESTINATIONS:
        check_doc = {
            "booking_id": booking_id,
            "user_id": user_id,
            "status": "Ready",
            "reason": "This is a domestic trip within India. Passport validity and visa requirements do not apply.",
            "created_at": datetime.datetime.utcnow().isoformat()
        }
        await document_checks_collection.update_one(
            {"booking_id": booking_id},
            {"$set": check_doc},
            upsert=True
        )
        return check_doc

    rule = PASSPORT_VALIDITY_MAP.get(dest_key, {"country": destination, "days": 180, "visa": "Please check visa requirements before travel."})
    
    country = rule["country"]
    min_days = rule["days"]
    visa_info = rule["visa"]

    try:
        end_dt = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
        passport_expiry_dt = datetime.datetime.strptime(passport_expiry_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dates must be in YYYY-MM-DD format."
        )

    # Passport must be valid for at least min_days beyond the return date
    required_validity_dt = end_dt + datetime.timedelta(days=min_days)
    
    if passport_expiry_dt >= required_validity_dt:
        status_result = "Ready"
        raw_reason = (
            f"Your passport is valid until {passport_expiry_str}, which satisfies the requirement of "
            f"minimum {min_days} days validity beyond your return date of {end_date_str} for {country}. "
            f"Visa info: {visa_info}"
        )
    else:
        days_short = (required_validity_dt - passport_expiry_dt).days
        status_result = "Action Needed"
        raw_reason = (
            f"Your passport will expire on {passport_expiry_str}, which is {days_short} days short of the required "
            f"{min_days} days validity beyond your return date of {end_date_str} for {country}. "
            f"You must renew your passport. Visa info: {visa_info}"
        )

    # Use LLM to phrase the reasoning conversationally
    prompt = f"""You are Journie, a professional AI travel booking assistant.
Rephrase the following passport and visa check result to be friendly, clear, and professional. 

Check Status: {status_result}
Details: {raw_reason}

Rules:
1. Do NOT use any emojis anywhere in the response.
2. Keep the explanation concise, helpful, and under 50 words.
3. Clearly state whether they are ready to go or need to renew their passport.
"""
    messages = [{"role": "user", "content": prompt}]
    
    try:
        phrased_reason = get_chat_completion(messages)
    except Exception as e:
        print(f"Error calling LLM for document check: {e}")
        # Fallback to the raw deterministic reason
        phrased_reason = raw_reason

    check_doc = {
        "booking_id": booking_id,
        "user_id": user_id,
        "status": status_result,
        "reason": phrased_reason,
        "created_at": datetime.datetime.utcnow().isoformat()
    }

    await document_checks_collection.update_one(
        {"booking_id": booking_id},
        {"$set": check_doc},
        upsert=True
    )
    return check_doc

async def get_booking_document_check(user_id: str, booking_id: str, booking_fallback: dict = None) -> dict:
    check = await document_checks_collection.find_one({"booking_id": booking_id})
    if check:
        check["id"] = str(check["_id"])
        del check["_id"]
        return check
        
    # If not found, compute dynamically (for seeded or pre-existing bookings)
    if booking_fallback:
        return await perform_document_check(
            user_id=user_id,
            booking_id=booking_id,
            destination=booking_fallback["destination"],
            end_date_str=booking_fallback["end_date"],
            passport_expiry_str=booking_fallback["passport_expiry"]
        )
    return {"status": "Action Needed", "reason": "No document checks found for this booking."}
