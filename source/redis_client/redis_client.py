# redis_client/redis_client.py
import time
import redis
from redis.exceptions import ConnectionError
from config.config import REDIS_HOST, REDIS_PORT, REDIS_DB

# High concurrency connection pool
_pool = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    max_connections=10000,
    decode_responses=True
)

class RedisClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = redis.Redis(connection_pool=_pool)
        return cls._instance

# Retry wrapper for transient Redis failures (e.g., network hiccups)
def retry_redis_call(fn, *args, retries=3, backoff=0.05, **kwargs):
    for attempt in range(retries):
        try:
            return fn(*args, **kwargs)
        except ConnectionError:
            time.sleep(backoff * (2 ** attempt))  # Exponential backoff
    # Final attempt (no catch)
    return fn(*args, **kwargs)


# Earlier code snippet, working!!!
# import redis
# from config.config import REDIS_HOST, REDIS_PORT, REDIS_DB

# class RedisClient:
#     _instance = None

#     def __new__(cls):
#         if cls._instance is None:
#             cls._instance = redis.Redis(
#                 host=REDIS_HOST,
#                 port=REDIS_PORT,
#                 db=REDIS_DB,
#                 decode_responses=True
#             )
#         return cls._instance
