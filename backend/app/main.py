from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
 
app = FastAPI(
    title="Journie API",
    description="One Stop Travel Genie",
    version="0.1.0",
)
 
import os

cors_origins = [
    "http://localhost:5173",  # Vite's default dev server port
    "http://127.0.0.1:5173",  # Vite served on loopback IP
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]
env_origins = os.getenv("CORS_ORIGINS")
if env_origins:
    cors_origins.extend([o.strip() for o in env_origins.split(",") if o.strip()])

# CORS: set up on Day 1, not Day 12 (per the roadmap's own warning — this bites
# everyone late in the project). Add your deployed Netlify URL here once you have it.
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"https://.*\.netlify\.app|https://.*\.vercel\.app|http://localhost:\d+|http://127\.0\.0\.1:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
 
@app.get("/")
async def root():
    """Quick sanity check — confirms the server is up."""
    return {"status": "Journie API is running"}
 
 
@app.get("/health")
async def health_check():
    """Used by Render (or any uptime check) to confirm the service is alive."""
    return {"status": "ok"}
 
from app.routes import chat_routes, auth_routes, booking_routes, group_trip_routes

app.include_router(chat_routes.router, prefix="/chat", tags=["chat"])
app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
app.include_router(booking_routes.router, prefix="/bookings", tags=["bookings"])
app.include_router(group_trip_routes.router, prefix="/group-trips", tags=["group-trips"])
