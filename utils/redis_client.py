#!/usr/bin/env python
# encoding: utf-8


from typing import Any, ClassVar

import redis
from redis import Redis


class RedisClient(object):
    _cli: ClassVar[Redis]

    @staticmethod
    def get_connection():
        return RedisClient._cli

    @staticmethod
    def connect(url: str):
        RedisClient._cli = redis.from_url(url=url)
        RedisClient._cli.ping()

    @staticmethod
    def get(key: str) -> Any:
        return RedisClient._cli.get(key)

    @staticmethod
    def set(key: str, value: Any, expire: int = 0):
        RedisClient._cli.set(key, value)
        if expire > 0:
            RedisClient._cli.expire(key, expire)

    @staticmethod
    def delete(key: str):
        RedisClient._cli.delete(key)

    @staticmethod
    def expire(key: str, expire: int):
        RedisClient._cli.expire(key, expire)

    @staticmethod
    def ping() -> Any:
        return RedisClient._cli.ping()
