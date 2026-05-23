#!/usr/bin/env python
# encoding: utf-8

from typing import Any, ClassVar, Optional
import asyncio
from redis import asyncio as aioredis
from redis.asyncio import Redis


class AsyncRedisClient(object):
    _cli: ClassVar[Optional[Redis]] = None
    _lock: ClassVar[asyncio.Lock] = asyncio.Lock()

    @staticmethod
    async def get_connection() -> Redis:
        if AsyncRedisClient._cli is None:
            async with AsyncRedisClient._lock:
                if AsyncRedisClient._cli is None:
                    raise RuntimeError("Redis client not initialized. Call connect() first.")
        return AsyncRedisClient._cli

    @staticmethod
    async def connect(url: str):
        async with AsyncRedisClient._lock:
            if AsyncRedisClient._cli is not None:
                return

            AsyncRedisClient._cli = await aioredis.from_url(
                url=url,
                encoding="utf-8",
                decode_responses=True
            )
            await AsyncRedisClient._cli.ping()

    @staticmethod
    async def get(key: str) -> Optional[str]:
        cli = await AsyncRedisClient.get_connection()
        return await cli.get(key)

    @staticmethod
    async def set(key: str, value: Any, expire: int = 0):
        cli = await AsyncRedisClient.get_connection()
        await cli.set(key, value)
        if expire > 0:
            await cli.expire(key, expire)

    @staticmethod
    async def delete(key: str):
        cli = await AsyncRedisClient.get_connection()
        await cli.delete(key)

    @staticmethod
    async def expire(key: str, expire: int):
        cli = await AsyncRedisClient.get_connection()
        await cli.expire(key, expire)

    @staticmethod
    async def ping() -> bool:
        cli = await AsyncRedisClient.get_connection()
        return await cli.ping()

    @staticmethod
    async def close():
        async with AsyncRedisClient._lock:
            if AsyncRedisClient._cli is not None:
                await AsyncRedisClient._cli.close()
                AsyncRedisClient._cli = None
