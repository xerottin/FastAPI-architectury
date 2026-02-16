from functools import lru_cache

from core.config import settings
from redis.asyncio import Redis


class RedisServices:
    @staticmethod
    @lru_cache
    def get_redis_client() -> Redis:
        return Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            encoding="utf-8",
        )
