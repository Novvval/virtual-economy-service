from typing import AsyncIterator

from redis.asyncio import Redis, from_url

from src.interfaces.cache import Cache


class RedisCache(Cache):
    def __init__(self, redis: Redis, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._redis = redis

    async def get(self, key: str, options: dict = None) -> str | None:
        return await self._redis.get(key)

    async def set(self, key: str, value: str, options: dict = None) -> None:
        options = options or {}
        ttl = options.get("ttl", None)
        await self._redis.set(key, value, ex=ttl)

    async def delete(self, key, options: dict = None) -> None:
        await self._redis.delete(key)

    async def iter(self, pattern: str, options: dict = None):
        options = options or {}
        count = options.get("count", None)
        async for key in self._redis.scan_iter(match=pattern, count=count):
            yield key


class InMemoryCache(Cache):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = {}

    async def get(self, key: str, options: dict = None) -> str | None:
        return self._cache.get(key)

    async def set(self, key: str, value: str, options: dict = None) -> None:
        self._cache[key] = value

    async def delete(self, key: str, options: dict = None) -> None:
        try:
            del self._cache[key]
        except KeyError:
            pass

    async def iter(self, pattern: str, options: dict = None):
        options = options or {}
        count = options.get("count", None)
        for key in self._cache.keys():
            if count is not None and count <= 0:
                break
            if pattern in key:
                yield key
                if count is not None:
                    count -= 1


async def init_redis_pool(host: str, port: str, password: str) -> AsyncIterator[Redis]:
    url = f"redis://{host}:{port}/0"
    session = from_url(url, password=password, encoding="utf-8", decode_responses=True)
    yield session
    session.close()
    await session.wait_closed()
