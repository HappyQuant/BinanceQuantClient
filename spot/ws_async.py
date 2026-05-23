#!/usr/bin/env python
# encoding: utf-8

import asyncio
import json
from typing import Optional, Callable, Awaitable

from binance import AsyncClient, BinanceSocketManager

from envs import Envs
from utils.redis_client_async import AsyncRedisClient
from utils.async_task_manager import AsyncTaskManager


class AsyncSpotWebSocket:
    def __init__(self, task_manager: AsyncTaskManager):
        self._client: Optional[AsyncClient] = None
        self._bsm: Optional[BinanceSocketManager] = None
        self._task_manager = task_manager
        self._lock = asyncio.Lock()

    async def _get_client(self) -> AsyncClient:
        if self._client is None:
            async with self._lock:
                if self._client is None:
                    Envs.initialize()
                    self._client = await AsyncClient.create(
                        api_key=Envs.ApiKey,
                        api_secret=Envs.ApiSecret
                    )
        return self._client

    async def _get_bsm(self) -> BinanceSocketManager:
        if self._bsm is None:
            async with self._lock:
                if self._bsm is None:
                    client = await self._get_client()
                    self._bsm = BinanceSocketManager(client)
        return self._bsm

    async def subscribe_partial_book_depth(
        self,
        symbol: str,
        levels: int = 5,
        update_speed: str = "100ms",
        redis_expire: int = 3
    ):
        bsm = await self._get_bsm()
        stop_event = self._task_manager.get_stop_event(f"spot_partial_book_{symbol}")

        async def message_handler():
            try:
                socket = bsm.partial_book_depth_socket(
                    symbol=symbol,
                    level=levels,
                    speed=update_speed
                )

                async with socket as stream:
                    while not stop_event.is_set():
                        try:
                            message = await asyncio.wait_for(
                                stream.recv(),
                                timeout=1.0
                            )
                            msg_obj = json.loads(message) if isinstance(message, str) else message
                            if "bids" in msg_obj and "asks" in msg_obj:
                                await AsyncRedisClient.set(
                                    f"spot_partial_book_{symbol}",
                                    message,
                                    redis_expire
                                )
                        except asyncio.TimeoutError:
                            continue
                        except Exception as e:
                            if not stop_event.is_set():
                                print(f"WebSocket error for {symbol}: {e}")
                                await asyncio.sleep(1)
            finally:
                await socket.__aexit__(None, None, None)

        return self._task_manager.create_task(
            message_handler(),
            name=f"spot_partial_book_{symbol}"
        )

    async def subscribe_aggregate_trade(
        self,
        symbol: str,
        on_message: Callable[[dict], Awaitable[None]]
    ):
        bsm = await self._get_bsm()
        stop_event = self._task_manager.get_stop_event(f"spot_agg_trade_{symbol}")

        async def message_handler():
            try:
                socket = bsm.aggregate_trade_socket(symbol=symbol)

                async with socket as stream:
                    while not stop_event.is_set():
                        try:
                            message = await asyncio.wait_for(
                                stream.recv(),
                                timeout=1.0
                            )
                            msg_obj = json.loads(message) if isinstance(message, str) else message
                            await on_message(msg_obj)
                        except asyncio.TimeoutError:
                            continue
                        except Exception as e:
                            if not stop_event.is_set():
                                print(f"WebSocket error for {symbol}: {e}")
                                await asyncio.sleep(1)
            finally:
                await socket.__aexit__(None, None, None)

        return self._task_manager.create_task(
            message_handler(),
            name=f"spot_agg_trade_{symbol}"
        )

    async def unsubscribe(self, symbol: str, stream_type: str):
        stop_event = self._task_manager.get_stop_event(f"spot_{stream_type}_{symbol}")
        stop_event.set()

    async def close(self):
        if self._bsm is not None:
            await self._bsm.close()
            self._bsm = None

        if self._client is not None:
            await self._client.close_connection()
            self._client = None

    async def __aenter__(self):
        await self._get_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


if __name__ == "__main__":
    async def main():
        Envs.load_from_env_file(".env")
        from utils.async_task_manager import AsyncTaskManager

        manager = AsyncTaskManager()
        await manager.start()

        ws = AsyncSpotWebSocket(manager)
        await ws.subscribe_partial_book_depth("BTCUSDT")

        try:
            await asyncio.sleep(30)
        finally:
            await manager.stop()
            await ws.close()

    asyncio.run(main())
