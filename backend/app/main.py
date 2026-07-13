from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
 
app = FastAPI(
    title="Journie API",
    description="One Stop Travel Genie",
    version="0.1.0",
)
 
# CORS: set up on Day 1, not Day 12 (per the roadmap's own warning — this bites
# everyone late in the project). Add your deployed Vercel URL here once you have it.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite's default dev server port
        # "https://tripmind.vercel.app",  # add your real deployed URL later
    ],
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
 
from app.routes import chat_routes, auth_routes, booking_routes

app.include_router(chat_routes.router, prefix="/chat", tags=["chat"])
app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
app.include_router(booking_routes.router, prefix="/bookings", tags=["bookings"])
