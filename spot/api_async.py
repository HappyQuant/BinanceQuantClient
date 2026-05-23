#!/usr/bin/env python
# encoding: utf-8

import asyncio
from enum import Enum
from typing import Optional, Dict, Any
import time

from binance import AsyncClient
from binance import enums

from envs import Envs


class TimeInForceEnum(Enum):
    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"


class AsyncSpotClient(object):
    def __init__(self):
        self._client: Optional[AsyncClient] = None
        self._lock = asyncio.Lock()

    async def _get_client(self) -> AsyncClient:
        if self._client is None:
            async with self._lock:
                if self._client is None:
                    Envs.initialize()
                    self._client = await AsyncClient.create(
                        api_key=Envs.ApiKey,
                        api_secret=Envs.ApiSecret,
                        requests_params={
                            "timeout": Envs.ClientTimeout,
                            "proxies": Envs.ClientProxy
                        }
                    )
        return self._client

    async def close(self):
        if self._client is not None:
            await self._client.close_connection()
            self._client = None

    async def get_spot_server_timestamp(self):
        client = await self._get_client()
        return await client.get_server_time()

    async def get_spot_exchange_info(self):
        client = await self._get_client()
        return await client.get_exchange_info()

    async def get_spot_trade_fee(self):
        client = await self._get_client()
        return await client.get_trade_fee()

    async def get_spot_ticker_price(self, symbol: str):
        client = await self._get_client()
        return await client.get_symbol_ticker(symbol=symbol)

    async def get_spot_balance(self):
        client = await self._get_client()
        return await client.get_account()

    async def get_spot_account(self):
        client = await self._get_client()
        return await client.get_account()

    async def get_spot_klines(self, symbol: str, interval: str, limit: int = 50,
                             end_time: Optional[int] = None):
        client = await self._get_client()
        if end_time is None:
            end_time = int(time.time() * 1000)
        return await client.get_klines(
            symbol=symbol,
            interval=interval,
            limit=limit,
            endTime=end_time
        )

    async def place_limit_order(self, symbol: str, side: str, price: float,
                                quantity: Optional[float] = None,
                                quoteOrderQty: Optional[float] = None,
                                timeInForce: TimeInForceEnum = TimeInForceEnum.GTC,
                                newClientOrderId: Optional[str] = None):
        client = await self._get_client()

        params: Dict[str, Any] = {
            "type": enums.ORDER_TYPE_LIMIT,
            "price": str(price),
            "timeInForce": timeInForce.value,
        }

        if quantity is not None:
            params["quantity"] = quantity
        elif quoteOrderQty is not None:
            params["quoteOrderQty"] = quoteOrderQty
        else:
            raise ValueError("Either quantity or quoteOrderQty must be provided")

        if newClientOrderId is not None:
            params["newClientOrderId"] = newClientOrderId

        return await client.create_order(
            symbol=symbol,
            side=side,
            **params
        )

    async def place_market_order(self, symbol: str, side: str,
                                 quantity: Optional[float] = None,
                                 quoteOrderQty: Optional[float] = None,
                                 newClientOrderId: Optional[str] = None):
        client = await self._get_client()

        params: Dict[str, Any] = {
            "type": enums.ORDER_TYPE_MARKET,
        }

        if quantity is not None:
            params["quantity"] = quantity
        elif quoteOrderQty is not None:
            params["quoteOrderQty"] = quoteOrderQty
        else:
            raise ValueError("Either quantity or quoteOrderQty must be provided")

        if newClientOrderId is not None:
            params["newClientOrderId"] = newClientOrderId

        return await client.create_order(
            symbol=symbol,
            side=side,
            **params
        )

    async def get_order(self, symbol: str, orderId: Optional[int] = None,
                        origClientOrderId: Optional[str] = None):
        client = await self._get_client()

        params: Dict[str, Any] = {"symbol": symbol}
        if orderId is not None:
            params["orderId"] = orderId
        elif origClientOrderId is not None:
            params["origClientOrderId"] = origClientOrderId
        else:
            raise ValueError("Either orderId or origClientOrderId must be provided")

        return await client.get_order(**params)

    async def cancel_order(self, symbol: str, orderId: Optional[int] = None,
                          origClientOrderId: Optional[str] = None):
        client = await self._get_client()

        params: Dict[str, Any] = {"symbol": symbol}
        if orderId is not None:
            params["orderId"] = orderId
        elif origClientOrderId is not None:
            params["origClientOrderId"] = origClientOrderId
        else:
            raise ValueError("Either orderId or origClientOrderId must be provided")

        return await client.cancel_order(**params)

    async def __aenter__(self):
        await self._get_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


if __name__ == "__main__":
    async def main():
        Envs.load_from_env_file(".env")
        c = AsyncSpotClient()
        print(await c.get_spot_server_timestamp())
        print(await c.get_spot_exchange_info())
        print(await c.get_spot_trade_fee())
        print(await c.get_spot_ticker_price("BTCUSDT"))
        print(await c.get_spot_balance())
        print(await c.get_spot_account())
        print(await c.get_spot_klines("BTCUSDT", "1s"))
        await c.close()

    asyncio.run(main())
