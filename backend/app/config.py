from pydantic_settings import BaseSettings
 
 
class Settings(BaseSettings):
    # Mongo
    mongo_uri: str
    mongo_db_name: str = "tripmind"
 
    # Groq LLM
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"
 
    # Auth (used from Day 4 onward)
    jwt_secret: str = "change-me-in-env"
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 60 * 24 * 7  # 7 days, generous for demo stability
 
    class Config:
        env_file = ".env"
 
 
# Import this single object everywhere instead of re-reading env vars
settings = Settings()