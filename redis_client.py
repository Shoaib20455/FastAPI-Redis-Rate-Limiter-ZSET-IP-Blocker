# redis_client.py
import redis
from config import REDIS_HOST, REDIS_PORT, REDIS_DB

# Redis client initialize kr rhy hain
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True  # Is se Redis bytes ki bajaye direct Python strings return krta hai
)

def get_redis():
    """Returns the Redis client."""
    return redis_client