#!/usr/bin/env python
# encoding: utf-8

import asyncio
from enum import Enum
from typing import Optional, Dict, Any
import time

from binance.um_futures import AsyncUMFutures

from envs import Envs


class UmTimeInForceEnum(Enum):
    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"


class AsyncUmFuturesClient(object):
    def __init__(self):
        self._client: Optional[AsyncUMFutures] = None
        self._lock = asyncio.Lock()

    async def _get_client(self) -> AsyncUMFutures:
        if self._client is None:
            async with self._lock:
                if self._client is None:
                    Envs.initialize()
                    self._client = AsyncUMFutures(
                        key=Envs.ApiKey,
                        secret=Envs.ApiSecret,
                        requests_params={
                            "timeout": Envs.ClientTimeout,
                            "proxies": Envs.ClientProxy
                        }
                    )
        return self._client

    async def close(self):
        if self._client is not None:
            await self._client.close_session()
            self._client = None

    async def get_um_futures_server_timestamp(self):
        client = await self._get_client()
        return await client.time()

    async def get_um_futures_exchange_info(self):
        client = await self._get_client()
        return await client.exchange_info()

    async def get_um_futures_ticker_price(self, symbol: str):
        client = await self._get_client()
        return await client.ticker_price(symbol=symbol)

    async def get_um_futures_book_ticker(self, symbol: str):
        client = await self._get_client()
        return await client.book_ticker(symbol=symbol)

    async def get_um_futures_balance(self):
        client = await self._get_client()
        return await client.balance()

    async def get_um_futures_account(self):
        client = await self._get_client()
        return await client.account()

    async def get_um_futures_funding_rate(self, symbol: str):
        client = await self._get_client()
        return await client.funding_rate(symbol=symbol)

    async def get_um_futures_klines(self, symbol: str, interval: str,
                                    limit: int = 50, end_time: Optional[int] = None):
        client = await self._get_client()
        if end_time is None:
            end_time = int(time.time() * 1000)
        params = {"symbol": symbol, "interval": interval, "limit": limit, "endTime": end_time}
        return await client.klines(**params)

    async def place_um_futures_limit_order(
        self, symbol: str, side: str, price: float, quantity: float,
        timeInForce: UmTimeInForceEnum = UmTimeInForceEnum.GTC,
        newClientOrderId: Optional[str] = None
    ):
        client = await self._get_client()

        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": "LIMIT",
            "timeInForce": timeInForce.value,
            "price": str(price),
            "quantity": str(quantity),
        }

        if newClientOrderId is not None:
            params["newClientOrderId"] = newClientOrderId

        return await client.new_order(**params)

    async def place_um_futures_market_order(
        self, symbol: str, side: str, quantity: float,
        newClientOrderId: Optional[str] = None
    ):
        client = await self._get_client()

        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": "MARKET",
            "quantity": str(quantity),
        }

        if newClientOrderId is not None:
            params["newClientOrderId"] = newClientOrderId

        return await client.new_order(**params)

    async def get_um_futures_order(
        self, symbol: str, orderId: Optional[int] = None,
        origClientOrderId: Optional[str] = None
    ):
        client = await self._get_client()

        params: Dict[str, Any] = {"symbol": symbol}
        if orderId is not None:
            params["orderId"] = orderId
        elif origClientOrderId is not None:
            params["origClientOrderId"] = origClientOrderId
        else:
            raise ValueError("Either orderId or origClientOrderId must be provided")

        return await client.query_order(**params)

    async def cancel_um_futures_order(
        self, symbol: str, orderId: Optional[int] = None,
        origClientOrderId: Optional[str] = None
    ):
        client = await self._get_client()

        params: Dict[str, Any] = {"symbol": symbol}
        if orderId is not None:
            params["orderId"] = orderId
        elif origClientOrderId is not None:
            params["origClientOrderId"] = origClientOrderId
        else:
            raise ValueError("Either orderId or origClientOrderId must be provided")

        return await client.cancel_order(**params)

    async def get_um_futures_position_risk(self, symbol: Optional[str] = None):
        client = await self._get_client()

        params: Dict[str, Any] = {}
        if symbol is not None:
            params["symbol"] = symbol

        return await client.get_position_risk(**params)

    async def __aenter__(self):
        await self._get_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


if __name__ == "__main__":
    async def main():
        Envs.load_from_env_file(".env")
        c = AsyncUmFuturesClient()
        print(await c.get_um_futures_server_timestamp())
        print(await c.get_um_futures_exchange_info())
        print(await c.get_um_futures_ticker_price("BTCUSDT"))
        print(await c.get_um_futures_book_ticker("BTCUSDT"))
        print(await c.get_um_futures_balance())
        print(await c.get_um_futures_account())
        print(await c.get_um_futures_funding_rate("BTCUSDT"))
        print(await c.get_um_futures_klines("BTCUSDT", "1m"))
        await c.close()

    asyncio.run(main())
