#!/usr/bin/env python
# encoding: utf-8

import asyncio
from enum import Enum
from typing import Optional, Dict, Any
import time

from binance import AsyncClient
from binance import enums

from envs import Envs


class CmTimeInForceEnum(Enum):
    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"


class AsyncCmFuturesClient(object):
    def __init__(self):
        self._client: Optional[AsyncClient] = None
        self._lock = asyncio.Lock()

    async def _get_client(self) -> AsyncClient:
        if self._client is None:
            async with self._lock:
                if self._client is None:
                    Envs.initialize()
                    proxy = Envs.ClientProxy.get("https") if Envs.ClientProxy else None
                    session_params = {}
                    if proxy:
                        session_params["proxy"] = proxy
                    self._client = await AsyncClient.create(
                        api_key=Envs.ApiKey,
                        api_secret=Envs.ApiSecret,
                        requests_params={
                            "timeout": Envs.ClientTimeout,
                        },
                        session_params=session_params
                    )
        return self._client

    async def close(self):
        if self._client is not None:
            await self._client.close_connection()
            self._client = None

    async def get_cm_futures_server_timestamp(self):
        client = await self._get_client()
        return await client.futures_coin_time()

    async def get_cm_futures_exchange_info(self):
        client = await self._get_client()
        return await client.futures_coin_exchange_info()

    async def get_cm_futures_ticker_price(self, symbol: str):
        client = await self._get_client()
        return await client.futures_coin_symbol_ticker(symbol=symbol)

    async def get_cm_futures_book_ticker(self, symbol: str):
        client = await self._get_client()
        return await client.futures_coin_orderbook_ticker(symbol=symbol)

    async def get_cm_futures_balance(self):
        client = await self._get_client()
        return await client.futures_coin_account_balance()

    async def get_cm_futures_account(self):
        client = await self._get_client()
        return await client.futures_coin_account()

    async def get_cm_futures_funding_rate(self, symbol: str):
        client = await self._get_client()
        return await client.futures_coin_funding_rate(symbol=symbol)

    async def get_cm_futures_klines(self, symbol: str, interval: str,
                                    limit: int = 50, end_time: Optional[int] = None):
        client = await self._get_client()
        if end_time is None:
            end_time = int(time.time() * 1000)
        return await client.futures_coin_klines(
            symbol=symbol,
            interval=interval,
            limit=limit,
            endTime=end_time
        )

    async def place_cm_futures_limit_order(
        self, symbol: str, side: str, price: float, quantity: float,
        timeInForce: CmTimeInForceEnum = CmTimeInForceEnum.GTC,
        newClientOrderId: Optional[str] = None
    ):
        client = await self._get_client()

        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": enums.FUTURE_ORDER_TYPE_LIMIT,
            "timeInForce": timeInForce.value,
            "price": str(price),
            "quantity": str(quantity),
        }

        if newClientOrderId is not None:
            params["newClientOrderId"] = newClientOrderId

        return await client.futures_coin_create_order(**params)

    async def place_cm_futures_market_order(
        self, symbol: str, side: str, quantity: float,
        newClientOrderId: Optional[str] = None
    ):
        client = await self._get_client()

        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": enums.FUTURE_ORDER_TYPE_MARKET,
            "quantity": str(quantity),
        }

        if newClientOrderId is not None:
            params["newClientOrderId"] = newClientOrderId

        return await client.futures_coin_create_order(**params)

    async def get_cm_futures_order(
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

        return await client.futures_coin_get_order(**params)

    async def cancel_cm_futures_order(
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

        return await client.futures_coin_cancel_order(**params)

    async def get_cm_futures_position_risk(self, symbol: Optional[str] = None):
        client = await self._get_client()

        params: Dict[str, Any] = {}
        if symbol is not None:
            params["symbol"] = symbol

        return await client.futures_coin_position_information(**params)

    async def __aenter__(self):
        await self._get_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


if __name__ == "__main__":
    async def main():
        Envs.load_from_env_file(".env")
        c = AsyncCmFuturesClient()
        print(await c.get_cm_futures_server_timestamp())
        print(await c.get_cm_futures_exchange_info())
        print(await c.get_cm_futures_ticker_price("BTCUSD_PERP"))
        print(await c.get_cm_futures_book_ticker("BTCUSD_PERP"))
        print(await c.get_cm_futures_balance())
        print(await c.get_cm_futures_account())
        print(await c.get_cm_futures_funding_rate("BTCUSD_PERP"))
        print(await c.get_cm_futures_klines("BTCUSD_PERP", "1m"))
        await c.close()

    asyncio.run(main())
