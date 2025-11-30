from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    JWT_ALGO: str = os.getenv("JWT_ALGO")
    JWT_EXP_MINUTES: int = int(os.getenv("JWT_EXP_MINUTES", 60))
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD") or None
    REDIS_CACHE_TTL: int = int(os.getenv("REDIS_CACHE_TTL", 60))
settings = Settings()