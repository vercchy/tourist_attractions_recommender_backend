import redis
from functools import lru_cache

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0


@lru_cache()
def get_redis_client():
    return redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
