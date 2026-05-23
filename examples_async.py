#!/usr/bin/env python
# encoding: utf-8
"""
BinanceQuant 异步 API 使用示例
"""

import asyncio
from envs import Envs
from spot import AsyncSpotClient
from futures import AsyncUmFuturesClient, AsyncCmFuturesClient
from utils import AsyncTaskManager, AsyncRedisClient
from spot.ws_async import AsyncSpotWebSocket
from futures.um_ws_async import AsyncUmFuturesWebSocket
from futures.cm_ws_async import AsyncCmFuturesWebSocket


async def spot_rest_example():
    """现货 REST API 异步示例"""
    print("=== 现货 REST API 示例 ===")
    client = AsyncSpotClient()

    try:
        # 获取服务器时间
        time = await client.get_spot_server_timestamp()
        print(f"Server time: {time}")

        # 获取交易对信息
        info = await client.get_spot_exchange_info()
        print(f"Exchange info: {len(info.get('symbols', []))} symbols")

        # 获取价格
        ticker = await client.get_spot_ticker_price("BTCUSDT")
        print(f"BTCUSDT price: {ticker}")

        # 获取 K 线
        klines = await client.get_spot_klines("BTCUSDT", "1m", limit=5)
        print(f"Klines count: {len(klines)}")

    finally:
        await client.close()


async def futures_rest_example():
    """期货 REST API 异步示例"""
    print("\n=== U 本位期货 REST API 示例 ===")
    client = AsyncUmFuturesClient()

    try:
        # 获取服务器时间
        time = await client.get_um_futures_server_timestamp()
        print(f"Server time: {time}")

        # 获取价格
        ticker = await client.get_um_futures_ticker_price("BTCUSDT")
        print(f"BTCUSDT price: {ticker}")

        # 获取账户信息
        account = await client.get_um_futures_account()
        print(f"Account: {account}")

    finally:
        await client.close()


async def websocket_example():
    """WebSocket 异步示例"""
    print("\n=== WebSocket 异步示例 ===")

    # 初始化环境
    Envs.initialize()
    await AsyncRedisClient.connect(Envs.RedisUrl)

    # 创建任务管理器
    manager = AsyncTaskManager()
    await manager.start()

    # 创建 WebSocket 客户端
    spot_ws = AsyncSpotWebSocket(manager)
    um_ws = AsyncUmFuturesWebSocket(manager)

    try:
        # 订阅现货深度
        await spot_ws.subscribe_partial_book_depth("BTCUSDT")
        print("订阅现货深度: BTCUSDT")

        # 订阅 U 本位期货深度
        await um_ws.subscribe_partial_book_depth("BTCUSDT")
        print("订阅 U 本位期货深度: BTCUSDT")

        # 从 Redis 读取数据
        await asyncio.sleep(2)
        spot_data = await AsyncRedisClient.get("spot_partial_book_BTCUSDT")
        um_data = await AsyncRedisClient.get("um_futures_partial_book_BTCUSDT")

        if spot_data:
            print(f"现货深度数据: {spot_data[:100]}...")
        if um_data:
            print(f"期货深度数据: {um_data[:100]}...")

        # 运行 10 秒
        print("\n运行 10 秒...")
        await asyncio.sleep(10)

    finally:
        await manager.stop()
        await spot_ws.close()
        await um_ws.close()
        await AsyncRedisClient.close()


async def concurrent_requests_example():
    """并发请求示例"""
    print("\n=== 并发请求示例 ===")

    client = AsyncSpotClient()

    try:
        # 并发获取多个交易对的价格
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT"]
        tasks = [client.get_spot_ticker_price(s) for s in symbols]

        results = await asyncio.gather(*tasks)

        for symbol, ticker in zip(symbols, results):
            print(f"{symbol}: {ticker}")

    finally:
        await client.close()


async def main():
    """主函数"""
    # 加载环境变量
    Envs.load_from_env_file(".env")

    # 运行各个示例
    await spot_rest_example()
    await futures_rest_example()
    await concurrent_requests_example()

    # WebSocket 示例（可选，需要 Redis）
    # await websocket_example()


if __name__ == "__main__":
    asyncio.run(main())
