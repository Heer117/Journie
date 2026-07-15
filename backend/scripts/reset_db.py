import asyncio
import os
import sys
import datetime
from bson import ObjectId

# Ensure backend root is on python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import (
    users_collection,
    hotels_collection,
    bookings_collection,
    document_checks_collection,
    group_trips_collection,
    conversations_collection
)
from app.utils.security import hash_password

HOTELS = [
    # Tokyo
    {
        "_id": ObjectId("60d5ec481f3b3b2f84e1b9a1"),
        "name": "The Ritz-Carlton, Tokyo",
        "destination": "Tokyo",
        "price_per_night": 650,
        "rating": 4.8,
        "image_url": "https://images.unsplash.com/photo-1549693578-d683be217e58?w=600&auto=format&fit=crop&q=60",
        "description": "Luxury hotel located in Midtown Tokyo with stunning panoramic views.",
        "tags": ["luxury", "spa", "near-transit", "views", "wifi"]
    },
    {
        "_id": ObjectId("60d5ec481f3b3b2f84e1b9a5"),
        "name": "Shinjuku Park Hotel",
        "destination": "Tokyo",
        "price_per_night": 120,
        "rating": 4.1,
        "image_url": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=600&q=80",
        "description": "Comfortable mid-range option near Shinjuku Station.",
        "tags": ["budget", "wifi", "city-center", "near-transit"]
    },
    {
        "_id": ObjectId("60d5ec481f3b3b2f84e1b9a6"),
        "name": "Capsule Inn Tokyo",
        "destination": "Tokyo",
        "price_per_night": 45,
        "rating": 3.9,
        "image_url": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=600&q=80",
        "description": "Authentic capsule hotel experience in the heart of Tokyo.",
        "tags": ["budget", "wifi", "solo-traveler", "near-transit"]
    },
    # Paris
    {
        "_id": ObjectId("60d5ec481f3b3b2f84e1b9a7"),
        "name": "Hotel Le Bristol",
        "destination": "Paris",
        "price_per_night": 850,
        "rating": 4.9,
        "image_url": "https://plus.unsplash.com/premium_photo-1718035557075-5111d9d906d2?w=600&auto=format&fit=crop&q=60",
        "description": "A historic palace hotel featuring a rooftop pool and exceptional service.",
        "tags": ["luxury", "pool", "spa", "romantic", "wifi"]
    },
    {
        "_id": ObjectId("60d5ec481f3b3b2f84e1b9a2"),
        "name": "Hotel Marais Paris",
        "destination": "Paris",
        "price_per_night": 190,
        "rating": 4.3,
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=600&q=80",
        "description": "Boutique hotel in the charming historic Marais district.",
        "tags": ["mid-range", "romantic", "wifi", "breakfast-included"]
    },
    {
        "_id": ObjectId("60d5ec481f3b3b2f84e1b9a8"),
        "name": "Generator Paris Hostel",
        "destination": "Paris",
        "price_per_night": 55,
        "rating": 4.0,
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=600&q=80",
        "description": "Social hostel with a rooftop terrace bar overlooking Montmartre.",
        "tags": ["budget", "wifi", "solo-traveler", "bar"]
    },
    # London
    {
        "_id": ObjectId("60d5ec481f3b3b2f84e1b9a9"),
        "name": "The Savoy",
        "destination": "London",
        "price_per_night": 720,
        "rating": 4.7,
        "image_url": "https://plus.unsplash.com/premium_photo-1682056762907-23d08f913805?q=80&w=600&auto=format&fit=crop",
        "description": "Iconic luxury hotel on the Strand with historical elegance.",
        "tags": ["luxury", "spa", "historic", "romantic", "wifi"]
    },
    {
        "_id": ObjectId("60d5ec481f3b3b2f84e1b9aa"),
        "name": "CitizenM Tower of London",
        "destination": "London",
        "price_per_night": 210,
        "rating": 4.5,
        "image_url": "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?auto=format&fit=crop&w=600&q=80",
        "description": "Modern hotel with smart rooms right next to the Tower of London.",
        "tags": ["mid-range", "wifi", "near-transit", "city-center"]
    },
    # Rome
    {
        "_id": ObjectId("60d5ec481f3b3b2f84e1b9ab"),
        "name": "Hotel de Russie",
        "destination": "Rome",
        "price_per_night": 800,
        "rating": 4.8,
        "image_url": "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=600&auto=format&fit=crop&q=60",
        "description": "Glamorous hotel near Piazza del Popolo with a gorgeous terraced garden.",
        "tags": ["luxury", "garden", "spa", "romantic", "wifi"]
    },
    {
        "_id": ObjectId("60d5ec481f3b3b2f84e1b9ac"),
        "name": "Hotel Smeraldo",
        "destination": "Rome",
        "price_per_night": 150,
        "rating": 4.3,
        "image_url": "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=600&auto=format&fit=crop&q=60",
        "description": "Cozy hotel located steps away from Campo de' Fiori.",
        "tags": ["mid-range", "city-center", "breakfast-included", "wifi"]
    },
    # New York
    {
        "_id": ObjectId("60d5ec481f3b3b2f84e1b9a3"),
        "name": "The Plaza",
        "destination": "New York",
        "price_per_night": 950,
        "rating": 4.8,
        "image_url": "https://images.unsplash.com/photo-1496588152823-86ff7695e68f?w=600&auto=format&fit=crop&q=60",
        "description": "World-famous luxury landmark off Central Park.",
        "tags": ["luxury", "historic", "spa", "romantic", "wifi"]
    },
    {
        "_id": ObjectId("60d5ec481f3b3b2f84e1b9ad"),
        "name": "Pod 39 Hotel",
        "destination": "New York",
        "price_per_night": 130,
        "rating": 4.1,
        "image_url": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?auto=format&fit=crop&w=600&q=80",
        "description": "Micro-rooms with high styling and a popular rooftop bar in Midtown.",
        "tags": ["budget", "wifi", "rooftop", "near-transit"]
    }
]

async def reset_db():
    print("--- Starting Full Database Clean-up ---")
    
    # 1. Drop existing documents in all collections
    await users_collection.delete_many({})
    await hotels_collection.delete_many({})
    await bookings_collection.delete_many({})
    await document_checks_collection.delete_many({})
    await group_trips_collection.delete_many({})
    await conversations_collection.delete_many({})
    
    print("Dropped all records from: users, hotels, bookings, document_checks, group_trips, conversations.")
    
    # 2. Seed default traveler user
    user_id = "60d5ec481f3b3b2f84e1b8c1"
    user_doc = {
        "_id": ObjectId(user_id),
        "name": "Demo Traveler",
        "email": "demo@journie.com",
        "password_hash": hash_password("Password123!")
    }
    await users_collection.insert_one(user_doc)
    print("Seeded Demo User: demo@journie.com / Password123!")
    
    # 3. Seed hotels
    await hotels_collection.insert_many(HOTELS)
    print(f"Seeded {len(HOTELS)} hotels directory options.")

    # Dates calculation helper
    today = datetime.date.today()
    
    # 4. Seed Bookings
    # Booking A: Active, Paris (Passport is valid - Ready)
    start_a = today + datetime.timedelta(days=10)
    end_a = today + datetime.timedelta(days=20)
    passport_a = today + datetime.timedelta(days=365)
    booking_id_a = "60d5ec481f3b3b2f84e1b7a1"
    
    booking_a = {
        "_id": ObjectId(booking_id_a),
        "user_id": user_id,
        "hotel_id": "60d5ec481f3b3b2f84e1b9a2", # Hotel Marais Paris
        "hotel_name": "Hotel Marais Paris",
        "destination": "Paris",
        "start_date": start_a.strftime("%Y-%m-%d"),
        "end_date": end_a.strftime("%Y-%m-%d"),
        "passport_expiry": passport_a.strftime("%Y-%m-%d"),
        "status": "active",
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    
    # Booking B: Active, New York (Passport expiring soon - Action Needed)
    start_b = today + datetime.timedelta(days=30)
    end_b = today + datetime.timedelta(days=35)
    passport_b = today + datetime.timedelta(days=15) # expires before return + 180 days!
    booking_id_b = "60d5ec481f3b3b2f84e1b7a2"
    
    booking_b = {
        "_id": ObjectId(booking_id_b),
        "user_id": user_id,
        "hotel_id": "60d5ec481f3b3b2f84e1b9a3", # The Plaza
        "hotel_name": "The Plaza",
        "destination": "New York",
        "start_date": start_b.strftime("%Y-%m-%d"),
        "end_date": end_b.strftime("%Y-%m-%d"),
        "passport_expiry": passport_b.strftime("%Y-%m-%d"),
        "status": "active",
        "created_at": datetime.datetime.utcnow().isoformat()
    }

    # Booking C: Cancelled, Tokyo (Cancelled badge, no check)
    start_c = today - datetime.timedelta(days=60)
    end_c = today - datetime.timedelta(days=55)
    passport_c = today + datetime.timedelta(days=180)
    booking_id_c = "60d5ec481f3b3b2f84e1b7a3"
    
    booking_c = {
        "_id": ObjectId(booking_id_c),
        "user_id": user_id,
        "hotel_id": "60d5ec481f3b3b2f84e1b9a1", # The Ritz-Carlton, Tokyo
        "hotel_name": "The Ritz-Carlton, Tokyo",
        "destination": "Tokyo",
        "start_date": start_c.strftime("%Y-%m-%d"),
        "end_date": end_c.strftime("%Y-%m-%d"),
        "passport_expiry": passport_c.strftime("%Y-%m-%d"),
        "status": "cancelled",
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    
    await bookings_collection.insert_many([booking_a, booking_b, booking_c])
    print("Seeded Bookings (1 Ready Paris, 1 Action Needed New York, 1 Cancelled Tokyo).")
    
    # 5. Seed Document Checks (only for active bookings A and B)
    doc_check_a = {
        "booking_id": booking_id_a,
        "user_id": user_id,
        "status": "Ready",
        "reason": f"Your passport is valid until {passport_a.strftime('%Y-%m-%d')}, which satisfies the Schengen area minimum 90 days validity requirement beyond your return date of {end_a.strftime('%Y-%m-%d')} for France. Visa info: Schengen visa-exempt for tourist stays up to 90 days.",
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    
    days_short = ((end_b + datetime.timedelta(days=180)) - passport_b).days
    doc_check_b = {
        "booking_id": booking_id_b,
        "user_id": user_id,
        "status": "Action Needed",
        "reason": f"Your passport will expire on {passport_b.strftime('%Y-%m-%d')}, which is {days_short} days short of the required 180 days validity beyond your return date of {end_b.strftime('%Y-%m-%d')} for the United States. You must renew your passport. Visa info: ESTA or tourist visa required.",
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    
    await document_checks_collection.insert_many([doc_check_a, doc_check_b])
    print("Seeded Document Check results for active Paris and New York bookings.")
    
    # 6. Seed Group Consensus Trip
    group_trip_id = "60d5ec481f3b3b2f84e1b6a1"
    group_trip = {
        "_id": ObjectId(group_trip_id),
        "user_id": user_id,
        "trip_name": "Summer in London with Friends",
        "destination": "London",
        "num_nights": 3,
        "members": [
            {"name": "Alice", "budget": 1000.0, "preferences": ["luxury", "spa"]},
            {"name": "Bob", "budget": 250.0, "preferences": ["wifi", "near-transit"]},
            {"name": "Charlie", "budget": 150.0, "preferences": ["wifi", "budget"]}
        ],
        "recommended_options": [
            {
                "hotel_id": "60d5ec481f3b3b2f84e1b9aa",
                "name": "CitizenM Tower of London",
                "price_per_night": 210.0,
                "rating": 4.5,
                "description": "Modern hotel with smart rooms right next to the Tower of London.",
                "tags": ["mid-range", "wifi", "near-transit", "city-center"],
                "per_person_cost": 210.0,
                "total_cost": 630.0,
                "score": 3,
                "member_matches": {
                    "Alice": ["wifi"],
                    "Bob": ["wifi", "near-transit"],
                    "Charlie": ["wifi"]
                }
            }
        ],
        "reasoning": "This consensus plan works perfectly because CitizenM Tower of London splits to $210 per night total (which is exactly $70 per person per night for 3 travelers), easily fitting within everyone's budget (including Bob's and Charlie's constraints). It matches Bob and Charlie's preferences for high-speed wifi and immediate transit links, and places the group right in the heart of London.",
        "status": "active",
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    await group_trips_collection.insert_one(group_trip)
    print("Seeded Group Trip Plan: 'Summer in London with Friends'")
    
    print("\nDatabase Reset and Seeding Completed Successfully!")

if __name__ == "__main__":
    asyncio.run(reset_db())
