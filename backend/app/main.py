from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat_routes

app = FastAPI(
    title="Journie API",
    description="One Stop Travel Genie",
    version="0.1.0",
)
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite's default dev server port
        # "https://journie.vercel.app",  # add your real deployed URL later
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
 
app.include_router(chat_routes.router, prefix="/chat", tags=["chat"])
