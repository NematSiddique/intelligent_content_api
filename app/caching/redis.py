from app.config import settings
import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT
REDIS_PASSWORD = settings.REDIS_PASSWORD
REDIS_DB = settings.REDIS_DB

def get_redis_client():
    try:

        client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            db=REDIS_DB,
            decode_responses=True
        )
        # Test connection
        client.ping()
        return client
    except Exception as e:
        print(f"Redis connection failed: {e}")
        return None

redis_client = get_redis_client()
