#!/usr/bin/env python
# encoding: utf-8
import time
from enum import Enum
from typing import Optional, Dict, Any

from binance import Client
from binance import enums

from envs import Envs
from gvars import GVars


class CmTimeInForceEnum(Enum):
    # Good Til Canceled
    GTC = "GTC"
    # Immediate Or Cancel
    IOC = "IOC"
    # Fill or Kill
    FOK = "FOK"


class CmFuturesClient(object):
    def __init__(self):
        Envs.initialize()
        GVars.initialize()
        self.client: Client = Client(
            api_key=Envs.ApiKey,
            api_secret=Envs.ApiSecret,
            requests_params={
                "timeout": Envs.ClientTimeout,
                "proxies": Envs.ClientProxy
            }
        )

    def get_cm_futures_server_timestamp(self):
        return self.client.futures_coin_time()

    def get_cm_futures_exchange_info(self):
        return self.client.futures_coin_exchange_info()

    def get_cm_futures_ticker_price(self, symbol: str):
        return self.client.futures_coin_symbol_ticker(symbol=symbol)

    def get_cm_futures_book_ticker(self, symbol: str):
        return self.client.futures_coin_orderbook_ticker(symbol=symbol)

    def get_cm_futures_balance(self):
        return self.client.futures_coin_account_balance()

    def get_cm_futures_account(self):
        return self.client.futures_coin_account()

    def get_cm_futures_funding_rate(self, symbol: str):
        return self.client.futures_coin_funding_rate(symbol=symbol)

    def get_cm_futures_klines(self, symbol: str, interval: str, limit: int = 50,
                              end_time: int = int(time.time() * 1000)):
        return self.client.futures_coin_klines(
            symbol=symbol,
            interval=interval,
            limit=limit,
            endTime=end_time
        )

    def place_cm_futures_limit_order(self, symbol: str, side: str, price: float, quantity: float,
                                     timeInForce: CmTimeInForceEnum = CmTimeInForceEnum.GTC,
                                     newClientOrderId: Optional[str] = None):
        params: Dict[str, Any] = {
            "timeInForce": timeInForce.value,
            "price": price,
            "quantity": quantity,
        }

        if newClientOrderId is not None:
            params["newClientOrderId"] = newClientOrderId
        return self.client.futures_coin_create_order(
            symbol=symbol,
            side=side,
            type=enums.FUTURE_ORDER_TYPE_LIMIT,
            **params
        )

    def place_cm_futures_market_order(self, symbol: str, side: str, quantity: float,
                                      newClientOrderId: Optional[str] = None):
        params: Dict[str, Any] = {
            "quantity": quantity,
        }

        if newClientOrderId is not None:
            params["newClientOrderId"] = newClientOrderId
        return self.client.futures_coin_create_order(
            symbol=symbol,
            side=side,
            type=enums.FUTURE_ORDER_TYPE_MARKET,
            **params
        )

    def get_cm_futures_order(self, symbol: str, orderId: Optional[int] = None, origClientOrderId: Optional[str] = None):
        params: Dict[str, Any] = {"symbol": symbol}
        if orderId is not None:
            params["orderId"] = orderId
        elif origClientOrderId is not None:
            params["origClientOrderId"] = origClientOrderId
        else:
            return None

        return self.client.futures_coin_get_order(**params)

    def cancel_cm_futures_order(self, symbol: str, orderId: Optional[int] = None,
                                origClientOrderId: Optional[str] = None):
        params: Dict[str, Any] = {"symbol": symbol}
        if orderId is not None:
            params["orderId"] = orderId
        elif origClientOrderId is not None:
            params["origClientOrderId"] = origClientOrderId
        else:
            return None

        return self.client.futures_coin_cancel_order(**params)

    def get_cm_futures_position_risk(self, symbol: Optional[str] = None):
        params: Dict[str, Any] = {}
        if symbol is not None:
            params["symbol"] = symbol

        return self.client.futures_coin_position_information(**params)


if __name__ == "__main__":
    Envs.load_from_env_file("../.env")
    c = CmFuturesClient()
    print(c.get_cm_futures_server_timestamp())
    print(c.get_cm_futures_exchange_info())
    print(c.get_cm_futures_ticker_price("BTCUSD_PERP"))
    print(c.get_cm_futures_book_ticker("BTCUSD_PERP"))
    print(c.get_cm_futures_balance())
    print(c.get_cm_futures_account())
    print(c.get_cm_futures_funding_rate("BTCUSD_PERP"))
    print(c.get_cm_futures_klines("BTCUSD_PERP", "1m"))
