import asyncio
import os
import sys
import random 
# Ensure backend root is on python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import hotels_collection

DESTINATION_IMAGES = {
    "Tokyo": [
        "https://images.unsplash.com/photo-1549693578-d683be217e58?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTR8fHRva3lvfGVufDB8fDB8fHww",
        "https://images.unsplash.com/photo-1549693578-d683be217e58?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTR8fHRva3lvfGVufDB8fDB8fHww",
    ],
    "Paris": [
        "https://plus.unsplash.com/premium_photo-1718035557075-5111d9d906d2?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NXx8cGFyaXN8ZW58MHx8MHx8fDA%3D",
    ],
    "London": [
        "https://plus.unsplash.com/premium_photo-1682056762907-23d08f913805?q=80&w=1074&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    ],
    "Rome": [
        "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8cm9tZXxlbnwwfHwwfHx8MA%3D%3D"
    ],
    "New York": [
        "https://images.unsplash.com/photo-1496588152823-86ff7695e68f?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8bmV3JTIweW9ya3xlbnwwfHwwfHx8MA%3D%3D"
    ]

  
}



HOTELS = [
    # Tokyo
    {
        "name": "The Ritz-Carlton, Tokyo",
        "destination": "Tokyo",
        "price_per_night": 650,
        "rating": 4.8,
        "image_url": random.choice(DESTINATION_IMAGES["Tokyo"]),
        "description": "Luxury hotel located in Midtown Tokyo with stunning panoramic views.",
        "tags": ["luxury", "spa", "near-transit", "views", "wifi"]
    },
    {
        "name": "Shinjuku Park Hotel",
        "destination": "Tokyo",
        "price_per_night": 120,
        "rating": 4.1,
        "description": "Comfortable mid-range option near Shinjuku Station.",
        "tags": ["budget", "wifi", "city-center", "near-transit"]
    },
    {
        "name": "Capsule Inn Tokyo",
        "destination": "Tokyo",
        "price_per_night": 45,
        "rating": 3.9,
        "description": "Authentic capsule hotel experience in the heart of Tokyo.",
        "tags": ["budget", "wifi", "solo-traveler", "near-transit"]
    },
    {
        "name": "Hotel Gracery Shinjuku",
        "destination": "Tokyo",
        "price_per_night": 180,
        "rating": 4.4,
        "description": "Famous Godzilla hotel with clean rooms and great views.",
        "tags": ["mid-range", "family-friendly", "wifi", "views"]
    },
    # Paris
    {
        "name": "Hotel Le Bristol",
        "destination": "Paris",
        "price_per_night": 850,
        "rating": 4.9,
        "image_url": random.choice(DESTINATION_IMAGES["Paris"]),
        "description": "A historic palace hotel featuring a rooftop pool and exceptional service.",
        "tags": ["luxury", "pool", "spa", "romantic", "wifi"]
    },
    {
        "name": "Hotel Marais Paris",
        "destination": "Paris",
        "price_per_night": 190,
        "rating": 4.3,
        "description": "Boutique hotel in the charming historic Marais district.",
        "tags": ["mid-range", "romantic", "wifi", "breakfast-included"]
    },
    {
        "name": "Generator Paris Hostel",
        "destination": "Paris",
        "price_per_night": 55,
        "rating": 4.0,
        "description": "Social hostel with a rooftop terrace bar overlooking Montmartre.",
        "tags": ["budget", "wifi", "solo-traveler", "bar"]
    },
    {
        "name": "Novotel Paris Les Halles",
        "destination": "Paris",
        "price_per_night": 240,
        "rating": 4.5,
        "description": "Family-friendly hotel with easy access to all central sights.",
        "tags": ["mid-range", "family-friendly", "gym", "wifi"]
    },
    # London
    {
        "name": "The Savoy",
        "destination": "London",
        "price_per_night": 720,
        "rating": 4.7,
        "image_url": random.choice(DESTINATION_IMAGES["London"]),
        "description": "Iconic luxury hotel on the Strand with historical elegance.",
        "tags": ["luxury", "spa", "historic", "romantic", "wifi"]
    },
    {
        "name": "CitizenM Tower of London",
        "destination": "London",
        "price_per_night": 210,
        "rating": 4.5,
        "description": "Modern hotel with smart rooms right next to the Tower of London.",
        "tags": ["mid-range", "wifi", "near-transit", "city-center"]
    },
    {
        "name": "Clink78 Hostel",
        "destination": "London",
        "price_per_night": 40,
        "rating": 3.7,
        "description": "Budget hostel set in a restored Victorian courthouse.",
        "tags": ["budget", "wifi", "solo-traveler", "historic"]
    },
    {
        "name": "Premier Inn London City",
        "destination": "London",
        "price_per_night": 110,
        "rating": 4.2,
        "description": "Reliable comfort for families visiting London's landmarks.",
        "tags": ["budget", "family-friendly", "breakfast-included", "wifi"]
    },
    # Rome
    {
        "name": "Hotel de Russie",
        "destination": "Rome",
        "price_per_night": 800,
        "rating": 4.8,
        "image_url": random.choice(DESTINATION_IMAGES["Rome"]),
        "description": "Glamorous hotel near Piazza del Popolo with a gorgeous terraced garden.",
        "tags": ["luxury", "garden", "spa", "romantic", "wifi"]
    },
    {
        "name": "Hotel Smeraldo",
        "destination": "Rome",
        "price_per_night": 150,
        "rating": 4.3,
        "description": "Cozy hotel located steps away from Campo de' Fiori.",
        "tags": ["mid-range", "city-center", "breakfast-included", "wifi"]
    },
    {
        "name": "Ostello Bello Roma",
        "destination": "Rome",
        "price_per_night": 50,
        "rating": 4.2,
        "description": "Lively hostel near the Colosseum with a great communal vibe.",
        "tags": ["budget", "wifi", "solo-traveler", "social"]
    },
    {
        "name": "Mercure Roma Centro Colosseo",
        "destination": "Rome",
        "price_per_night": 190,
        "rating": 4.4,
        "description": "Mid-range hotel boasting a seasonal rooftop pool facing the Colosseum.",
        "tags": ["mid-range", "pool", "near-transit", "views", "wifi"]
    },
    # New York
    {
        "name": "The Plaza",
        "destination": "New York",
        "price_per_night": 950,
        "rating": 4.8,
        "image_url": random.choice(DESTINATION_IMAGES["New York"]),
        "description": "World-famous luxury landmark off Central Park.",
        "tags": ["luxury", "historic", "spa", "romantic", "wifi"]
    },
    {
        "name": "Pod 39 Hotel",
        "destination": "New York",
        "price_per_night": 130,
        "rating": 4.1,
        "description": "Micro-rooms with high styling and a popular rooftop bar in Midtown.",
        "tags": ["budget", "wifi", "rooftop", "near-transit"]
    },
    {
        "name": "Arlo NoMad",
        "destination": "New York",
        "price_per_night": 220,
        "rating": 4.3,
        "description": "Micro-hotel with sweeping city views and a chic rooftop deck.",
        "tags": ["mid-range", "views", "rooftop", "wifi"]
    },
    {
        "name": "Freehand New York",
        "destination": "New York",
        "price_per_night": 170,
        "rating": 4.2,
        "description": "Chic, artistic hotel located in Flatiron.",
        "tags": ["mid-range", "historic", "gym", "bar", "wifi"]
    }
]

async def main():
    print("Clearing hotels collection...")
    await hotels_collection.delete_many({})
    print(f"Inserting {len(HOTELS)} hotels...")
    result = await hotels_collection.insert_many(HOTELS)
    print(f"Seeded successfully! Inserted IDs: {len(result.inserted_ids)}")

if __name__ == "__main__":
    asyncio.run(main())
