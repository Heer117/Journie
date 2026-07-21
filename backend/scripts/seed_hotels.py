import asyncio
import os
import sys
import random

# Ensure backend root is on python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import hotels_collection

# 2-3 curated real photo URLs per destination
DESTINATION_IMAGES = {
    "Tokyo": [
        "https://images.unsplash.com/photo-1549693578-d683be217e58?w=600&auto=format&fit=crop&q=60",
        "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=600&auto=format&fit=crop&q=60"
    ],
    "Paris": [
        "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=600&auto=format&fit=crop&q=60",
        "https://plus.unsplash.com/premium_photo-1718035557075-5111d9d906d2?w=600&auto=format&fit=crop&q=60"
    ],
    "London": [
        "https://plus.unsplash.com/premium_photo-1682056762907-23d08f913805?q=80&w=600&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=600&auto=format&fit=crop&q=60"
    ],
    "Rome": [
        "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=600&auto=format&fit=crop&q=60",
        "https://images.unsplash.com/photo-1529260830199-445804537968?w=600&auto=format&fit=crop&q=60"
    ],
    "New York": [
        "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=600&auto=format&fit=crop&q=60",
        "https://images.unsplash.com/photo-1496588152823-86ff7695e68f?w=600&auto=format&fit=crop&q=60"
    ],
    "Goa": [
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=600&auto=format&fit=crop&q=60",
        "https://images.unsplash.com/photo-1519046904884-53103b34b206?w=600&auto=format&fit=crop&q=60"
    ],
    "Manali": [
        "https://images.unsplash.com/photo-1626896756165-247e62a149b6?w=600&auto=format&fit=crop&q=60",
        "https://images.unsplash.com/photo-1605649487212-47bdab064df7?w=600&auto=format&fit=crop&q=60"
    ],
    "Jaipur": [
        "https://images.unsplash.com/photo-1477584308802-e9c3788ee1a4?w=600&auto=format&fit=crop&q=60",
        "https://images.unsplash.com/photo-1599661046289-e31897846e41?w=600&auto=format&fit=crop&q=60"
    ],
    "Udaipur": [
        "https://images.unsplash.com/photo-1566552881560-0be862a7c445?w=600&auto=format&fit=crop&q=60",
        "https://images.unsplash.com/photo-1603258837072-5b94f1c1fdf6?w=600&auto=format&fit=crop&q=60"
    ],
    "Kerala": [
        "https://images.unsplash.com/photo-1593693397690-362cb9666fc2?w=600&auto=format&fit=crop&q=60",
        "https://images.unsplash.com/photo-1543731068-7e0f5beff43a?w=600&auto=format&fit=crop&q=60"
    ],
    "Rishikesh": [
        "https://images.unsplash.com/photo-1545638190-2751f8920d23?w=600&auto=format&fit=crop&q=60",
        "https://images.unsplash.com/photo-1605649487212-47bdab064df7?w=600&auto=format&fit=crop&q=60"
    ],
    "Thailand": [
        "https://images.unsplash.com/photo-1528181304800-2f1702425221?w=600&auto=format&fit=crop&q=60",
        "https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?w=600&auto=format&fit=crop&q=60"
    ],
    "Dubai": [
        "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=600&auto=format&fit=crop&q=60",
        "https://images.unsplash.com/photo-1582672060674-bc2bd808a8b5?w=600&auto=format&fit=crop&q=60"
    ],
    "Singapore": [
        "https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=600&auto=format&fit=crop&q=60",
        "https://images.unsplash.com/photo-1506461883276-594a12b11cc3?w=600&auto=format&fit=crop&q=60"
    ],
    "Bali": [
        "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=600&auto=format&fit=crop&q=60",
        "https://images.unsplash.com/photo-1552674605-db6ffd4facb5?w=600&auto=format&fit=crop&q=60"
    ],
    "Switzerland": [
        "https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?w=600&auto=format&fit=crop&q=60",
        "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=600&auto=format&fit=crop&q=60"
    ],
    "Maldives": [
        "https://images.unsplash.com/photo-1439066615861-d1af74d74000?w=600&auto=format&fit=crop&q=60",
        "https://images.unsplash.com/photo-1505118380757-91f5f5632de0?w=600&auto=format&fit=crop&q=60"
    ]
}

# 17 destinations total (6 domestic, 11 international)
# 4 unique hotels per destination with realistic varied pricing, ratings, descriptions, and tags.
HOTELS = []

# Helper to populate HOTELS list
def add_hotel(name, destination, price, rating, desc, tags):
    HOTELS.append({
        "name": name,
        "destination": destination,
        "price_per_night": price,
        "rating": rating,
        "image_url": random.choice(DESTINATION_IMAGES[destination]),
        "description": desc,
        "tags": tags
    })

# Existing 5 Destinations:
# Tokyo
add_hotel("The Ritz-Carlton, Tokyo", "Tokyo", 650, 4.8, "Luxury hotel located in Midtown Tokyo with stunning panoramic views.", ["luxury", "spa", "near-transit", "views", "wifi"])
add_hotel("Shinjuku Park Hotel", "Tokyo", 120, 4.1, "Comfortable mid-range option near Shinjuku Station.", ["budget", "wifi", "city-center", "near-transit"])
add_hotel("Capsule Inn Tokyo", "Tokyo", 45, 3.9, "Authentic capsule hotel experience in the heart of Tokyo.", ["budget", "wifi", "solo-traveler", "near-transit"])
add_hotel("Hotel Gracery Shinjuku", "Tokyo", 180, 4.4, "Famous Godzilla hotel with clean rooms and great views.", ["mid-range", "family-friendly", "wifi", "views"])

# Paris
add_hotel("Hotel Le Bristol", "Paris", 850, 4.9, "A historic palace hotel featuring a rooftop pool and exceptional service.", ["luxury", "pool", "spa", "romantic", "wifi"])
add_hotel("Hotel Marais Paris", "Paris", 190, 4.3, "Boutique hotel in the charming historic Marais district.", ["mid-range", "romantic", "wifi", "breakfast-included"])
add_hotel("Generator Paris Hostel", "Paris", 55, 4.0, "Social hostel with a rooftop terrace bar overlooking Montmartre.", ["budget", "wifi", "solo-traveler", "bar"])
add_hotel("Novotel Paris Les Halles", "Paris", 240, 4.5, "Family-friendly hotel with easy access to all central sights.", ["mid-range", "family-friendly", "gym", "wifi"])

# London
add_hotel("The Savoy", "London", 720, 4.7, "Iconic luxury hotel on the Strand with historical elegance.", ["luxury", "spa", "historic", "romantic", "wifi"])
add_hotel("CitizenM Tower of London", "London", 210, 4.5, "Modern hotel with smart rooms right next to the Tower of London.", ["mid-range", "wifi", "near-transit", "city-center"])
add_hotel("Clink78 Hostel", "London", 40, 3.7, "Budget hostel set in a restored Victorian courthouse.", ["budget", "wifi", "solo-traveler", "historic"])
add_hotel("Premier Inn London City", "London", 110, 4.2, "Reliable comfort for families visiting London's landmarks.", ["budget", "family-friendly", "breakfast-included", "wifi"])

# Rome
add_hotel("Hotel de Russie", "Rome", 800, 4.8, "Glamorous hotel near Piazza del Popolo with a gorgeous terraced garden.", ["luxury", "garden", "spa", "romantic", "wifi"])
add_hotel("Hotel Smeraldo", "Rome", 150, 4.3, "Cozy hotel located steps away from Campo de' Fiori.", ["mid-range", "city-center", "breakfast-included", "wifi"])
add_hotel("Ostello Bello Roma", "Rome", 50, 4.2, "Lively hostel near the Colosseum with a great communal vibe.", ["budget", "wifi", "solo-traveler", "social"])
add_hotel("Mercure Roma Centro Colosseo", "Rome", 190, 4.4, "Mid-range hotel boasting a seasonal rooftop pool facing the Colosseum.", ["mid-range", "pool", "near-transit", "views", "wifi"])

# New York
add_hotel("The Plaza", "New York", 950, 4.8, "World-famous luxury landmark off Central Park.", ["luxury", "historic", "spa", "romantic", "wifi"])
add_hotel("Pod 39 Hotel", "New York", 130, 4.1, "Micro-rooms with high styling and a popular rooftop bar in Midtown.", ["budget", "wifi", "rooftop", "near-transit"])
add_hotel("Arlo NoMad", "New York", 220, 4.3, "Micro-hotel with sweeping city views and a chic rooftop deck.", ["mid-range", "views", "rooftop", "wifi"])
add_hotel("Freehand New York", "New York", 170, 4.2, "Chic, artistic hotel located in Flatiron.", ["mid-range", "historic", "gym", "bar", "wifi"])

# 12 New Destinations:
# Domestic (6): Goa, Manali, Jaipur, Udaipur, Kerala, Rishikesh
# Goa
add_hotel("Taj Exotica Resort & Spa, Goa", "Goa", 18000, 4.8, "Luxury Mediterranean-style oasis overlooking the Arabian Sea.", ["luxury", "spa", "pool", "beach", "wifi"])
add_hotel("Bella Vista Guest House", "Goa", 2500, 4.2, "Cozy budget guest house located within walking distance to the beach.", ["budget", "wifi", "beach"])
add_hotel("Whispering Palms Beach Resort", "Goa", 7500, 4.4, "Family-friendly resort with great amenities, pool, and dining.", ["mid-range", "family-friendly", "pool", "wifi"])
add_hotel("Goa Heritage Hostel", "Goa", 1200, 4.0, "Vibrant backpacker hostel with a lively garden and social lounge.", ["budget", "social", "solo-traveler", "wifi"])

# Manali
add_hotel("Solang Valley Resort", "Manali", 12000, 4.6, "Stunning luxury resort nestled amidst the snow-capped Himalayan peaks.", ["luxury", "views", "family-friendly", "wifi"])
add_hotel("Snow Creste Manor", "Manali", 4500, 4.1, "Comfortable hotel offering breathtaking valley views and clean rooms.", ["mid-range", "views", "wifi"])
add_hotel("Backpacker's Nest Manali", "Manali", 1500, 4.3, "Budget hostel with a community kitchen and views of the Beas River.", ["budget", "solo-traveler", "social", "wifi"])
add_hotel("Span Resort & Spa", "Manali", 22000, 4.8, "Ultra-luxury riverside resort featuring a premier spa and pools.", ["luxury", "spa", "pool", "views", "wifi"])

# Jaipur
add_hotel("The Rambagh Palace", "Jaipur", 35000, 4.9, "Palatial luxury stay with grand royal gardens and heritage architecture.", ["luxury", "historic", "spa", "pool", "wifi"])
add_hotel("Umaid Bhawan Hotel", "Jaipur", 5000, 4.4, "Mid-range heritage hotel with beautiful wall paintings and a pool.", ["mid-range", "historic", "pool", "wifi"])
add_hotel("Zostel Jaipur", "Jaipur", 1000, 4.2, "Social budget hostel located in the heart of the old city.", ["budget", "social", "city-center", "wifi"])
add_hotel("Pearl Palace Heritage", "Jaipur", 4000, 4.5, "Artistic boutique hotel showcasing Rajasthan's rich cultural themes.", ["mid-range", "historic", "art", "wifi"])

# Udaipur
add_hotel("The Taj Lake Palace", "Udaipur", 40000, 4.9, "Iconic luxury heritage hotel floating in the middle of Lake Pichola.", ["luxury", "views", "historic", "pool", "romantic", "wifi"])
add_hotel("Lake Pichola Hotel", "Udaipur", 6000, 4.3, "Charming mid-range lakeside hotel offering spectacular sunset views.", ["mid-range", "views", "romantic", "wifi"])
add_hotel("Mewar Castle Guest House", "Udaipur", 1800, 4.1, "Budget guest house with a rooftop restaurant overlooking the lake.", ["budget", "views", "wifi"])
add_hotel("Radisson Blu Udaipur Palace Resort", "Udaipur", 12000, 4.5, "Premium lakeview resort with a spacious multi-tier pool and dining.", ["luxury", "pool", "family-friendly", "wifi"])

# Kerala
add_hotel("Kumarakom Lake Resort", "Kerala", 24000, 4.8, "Luxury backwater resort with heritage villas and meandering pools.", ["luxury", "pool", "spa", "views", "wifi"])
add_hotel("Munnar Tea Hills Resort", "Kerala", 5500, 4.3, "Scenic mid-range resort surrounded by green Munnar tea gardens.", ["mid-range", "views", "family-friendly", "wifi"])
add_hotel("Fort Kochi Hostel", "Kerala", 1200, 4.1, "Budget hostel within walking distance to famous Chinese fishing nets.", ["budget", "solo-traveler", "social", "wifi"])
add_hotel("Lake Canopy Alleppey", "Kerala", 7000, 4.4, "Charming lakefront cottages featuring premium family-friendly amenities.", ["mid-range", "pool", "views", "wifi"])

# Rishikesh
add_hotel("Ananda in the Himalayas", "Rishikesh", 38000, 4.9, "World-renowned luxury destination spa in the foothills of the Himalayas.", ["luxury", "spa", "views", "wellness", "wifi"])
add_hotel("Aloha on the Ganges", "Rishikesh", 11000, 4.6, "Beautiful riverside resort with yoga centers and an infinity pool.", ["luxury", "pool", "views", "family-friendly", "wifi"])
add_hotel("Zostel Rishikesh", "Rishikesh", 1100, 4.3, "Vibrant hostel offering panoramic mountain views and social vibes.", ["budget", "social", "views", "solo-traveler", "wifi"])
add_hotel("Divine Resort & Spa", "Rishikesh", 5500, 4.2, "Cozy mid-range hotel directly overlooking the holy river Ganges.", ["mid-range", "spa", "views", "wifi"])

# International (6): Thailand, Dubai, Singapore, Bali, Switzerland, Maldives
# Thailand
add_hotel("Mandarin Oriental, Bangkok", "Thailand", 450, 4.9, "Legendary hotel on the banks of Chao Phraya River.", ["luxury", "spa", "views", "pool", "wifi"])
add_hotel("Phuket Beachside Resort", "Thailand", 120, 4.2, "Relaxing beachfront resort with pools and massage services.", ["mid-range", "pool", "romantic", "wifi"])
add_hotel("Lub d Bangkok Siam", "Thailand", 35, 4.1, "Funky design hostel located in the prime shopping district of Siam.", ["budget", "social", "solo-traveler", "wifi"])
add_hotel("Novotel Phuket Resort", "Thailand", 160, 4.4, "Family-friendly resort with dynamic pools and views of Patong Bay.", ["mid-range", "family-friendly", "pool", "views", "wifi"])

# Dubai
add_hotel("Burj Al Arab Jumeirah", "Dubai", 1500, 4.9, "Ultra-luxury sail-shaped landmark hotel built on its own island.", ["luxury", "views", "beach", "spa", "pool", "wifi"])
add_hotel("Rove Downtown Dubai", "Dubai", 130, 4.5, "Modern, trendy hotel located steps away from the Burj Khalifa.", ["mid-range", "city-center", "pool", "near-transit", "wifi"])
add_hotel("Dubai Youth Hostel", "Dubai", 40, 3.8, "Clean, budget-friendly hostel with a large outdoor pool.", ["budget", "wifi", "pool"])
add_hotel("Atlantis The Palm", "Dubai", 650, 4.8, "Famous resort featuring an underwater aquarium and waterpark.", ["luxury", "pool", "family-friendly", "views", "wifi"])

# Singapore
add_hotel("Marina Bay Sands", "Singapore", 700, 4.8, "World-famous hotel with the largest rooftop infinity pool.", ["luxury", "pool", "views", "city-center", "wifi"])
add_hotel("Hotel Mono", "Singapore", 140, 4.2, "Minimalist chic hotel set in a restored Chinatown shophouse.", ["mid-range", "design", "city-center", "wifi"])
add_hotel("Capsule Pod Singapore", "Singapore", 45, 4.0, "Futuristic capsule sleeping pod located near transit links.", ["budget", "wifi", "solo-traveler"])
add_hotel("Orchard Rendezvous Hotel", "Singapore", 190, 4.3, "Comfortable family-friendly hotel in Singapore's premier shopping street.", ["mid-range", "family-friendly", "pool", "wifi"])

# Bali
add_hotel("Ayana Resort and Spa, Bali", "Bali", 380, 4.8, "Cliff-top resort overlooking Jimbaran Bay with stunning ocean views.", ["luxury", "pool", "spa", "views", "romantic", "wifi"])
add_hotel("Ubud Green Resort", "Bali", 110, 4.3, "Peaceful boutique resort surrounded by green rice terraces.", ["mid-range", "views", "romantic", "pool", "wifi"])
add_hotel("Lay Day Surf Hostel", "Bali", 25, 4.1, "Lively backpacker hostel with two pools, surf trips, and social bar.", ["budget", "social", "pool", "solo-traveler", "wifi"])
add_hotel("Grand Hyatt Bali", "Bali", 220, 4.5, "Resort styled as a Balinese water palace on Nusa Dua beach.", ["luxury", "pool", "family-friendly", "beach", "wifi"])

# Switzerland
add_hotel("The Dolder Grand, Zurich", "Switzerland", 750, 4.9, "Historic landmark hotel with a world-class art collection and spa.", ["luxury", "spa", "views", "pool", "wifi"])
add_hotel("Hotel Central Luzern", "Switzerland", 180, 4.2, "Boutique hotel with modern rooms located next to Lake Lucerne.", ["mid-range", "city-center", "near-transit", "wifi"])
add_hotel("Backpackers Villa Sonnenhof", "Switzerland", 60, 4.4, "Budget-friendly hostel in Interlaken with panoramic alpine views.", ["budget", "social", "views", "family-friendly", "wifi"])
add_hotel("Grand Hotel National Luzern", "Switzerland", 420, 4.7, "Stately grand hotel overlooking Lake Lucerne with absolute luxury.", ["luxury", "views", "pool", "historic", "wifi"])

# Maldives
add_hotel("Soneva Jani", "Maldives", 1800, 4.9, "Ultra-luxury overwater villas featuring retractable roofs and water slides.", ["luxury", "pool", "water-villa", "spa", "views", "romantic", "wifi"])
add_hotel("Meeru Island Resort & Spa", "Maldives", 450, 4.7, "Superb island resort with white sandy beaches and turquoise lagoons.", ["luxury", "beach", "pool", "spa", "family-friendly", "wifi"])
add_hotel("Maafushi Village Guest House", "Maldives", 65, 4.1, "Charming budget guest house steps away from local bikini beach.", ["budget", "beach", "wifi"])
add_hotel("Arena Beach Hotel", "Maldives", 130, 4.4, "Modern beachfront hotel featuring rooftop pool and sunset views.", ["mid-range", "beach", "pool", "views", "wifi"])


async def main():
    # Requirement: Show full destination list before generating/updating data
    print("==========================================================")
    print("Starting Hotel Data Seeding Process...")
    print("Full Destination List to be Registered:")
    print("  - Domestic Destinations (6):")
    print("      Goa, Manali, Jaipur, Udaipur, Kerala, Rishikesh")
    print("  - International Destinations (11):")
    print("      Tokyo, Paris, London, Rome, New York, Thailand, Dubai, Singapore, Bali, Switzerland, Maldives")
    print("==========================================================")
    
    print(f"Upserting {len(HOTELS)} hotels alongside existing dataset...")
    count_updated = 0
    count_inserted = 0
    
    for hotel in HOTELS:
        # Check if the hotel already exists by name and destination
        existing = await hotels_collection.find_one({
            "name": hotel["name"],
            "destination": hotel["destination"]
        })
        
        if existing:
            # Update existing document but keep the same _id
            await hotels_collection.update_one(
                {"_id": existing["_id"]},
                {"$set": hotel}
            )
            count_updated += 1
        else:
            # Insert as a new document
            await hotels_collection.insert_one(hotel)
            count_inserted += 1
            
    print(f"Seeding completed successfully!")
    print(f"Total Hotels Processed: {len(HOTELS)}")
    print(f"  - Newly Inserted: {count_inserted}")
    print(f"  - Updated Existing: {count_updated}")
    print("==========================================================")

if __name__ == "__main__":
    asyncio.run(main())
