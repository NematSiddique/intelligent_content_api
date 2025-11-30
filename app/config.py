from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    JWT_ALGO: str = os.getenv("JWT_ALGO")
    JWT_EXP_MINUTES: int = int(os.getenv("JWT_EXP_MINUTES", 60))
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
settings = Settings()