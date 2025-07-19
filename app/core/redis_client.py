import redis.asyncio as redis 
import os

# Redis connection 
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST','localhost'),  # or "redis" if inside docker-compose.
    port=6379,
    db=0,
    decode_responses=True
)
