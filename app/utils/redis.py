import redis.asyncio as redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

async def get_redis_client():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
