#!/usr/bin/env python
# encoding: utf-8
import time
from enum import Enum
from typing import Optional, Dict, Any

from binance.um_futures import UMFutures, market, account

from envs import Envs
from gvars import GVars


class UmTimeInForceEnum(Enum):
    # Good Til Canceled
    GTC = "GTC"
    # Immediate Or Cancel
    IOC = "IOC"
    # Fill or Kill
    FOK = "FOK"


class UmFuturesClient(object):
    def __init__(self):
        Envs.initialize()
        GVars.initialize()
        self.client: UMFutures = UMFutures(Envs.ApiKey, Envs.ApiSecret,
                                           timeout=Envs.ClientTimeout, show_limit_usage=Envs.ClientShowLimit,
                                           show_header=Envs.ClientShowHeader, proxies=Envs.ClientProxy)

    def get_um_futures_server_timestamp(self):
        return market.time(self.client)

    def get_um_futures_exchange_info(self):
        return market.exchange_info(self.client)

    def get_um_futures_ticker_price(self, symbol: str):
        return market.ticker_price(self.client, symbol)

    def get_um_futures_book_ticker(self, symbol: str):
        return market.book_ticker(self.client, symbol)

    def get_um_futures_balance(self):
        return account.balance(self.client)

    def get_um_futures_account(self):
        return account.account(self.client)

    def get_um_futures_funding_rate(self, symbol: str):
        return market.funding_rate(self.client, symbol)

    def get_um_futures_klines(self, symbol: str, interval: str, limit: int = 50,
                              end_time: int = int(time.time() * 1000)):
        return market.klines(self.client, symbol, interval, limit=limit, endTime=end_time)

    def place_um_futures_limit_order(self, symbol: str, side: str, price: float, quantity: float,
                                     timeInForce: UmTimeInForceEnum = UmTimeInForceEnum.GTC,
                                     newClientOrderId: Optional[str] = None):
        params: Dict[str, Any] = {
            "timeInForce": timeInForce.value,
            "price": price,
            "quantity": quantity,
        }

        if newClientOrderId is not None:
            params["newClientOrderId"] = newClientOrderId
        return account.new_order(self.client, symbol, side, "LIMIT", **params)

    def place_um_futures_market_order(self, symbol: str, side: str, quantity: float,
                                      newClientOrderId: Optional[str] = None):
        params: Dict[str, Any] = {
            "quantity": quantity,
        }

        if newClientOrderId is not None:
            params["newClientOrderId"] = newClientOrderId
        return account.new_order(self.client, symbol, side, "MARKET", **params)

    def get_um_futures_order(self, symbol: str, orderId: Optional[int] = None, origClientOrderId: Optional[str] = None):
        params: Dict[str, Any] = dict()
        if orderId is not None:
            params["orderId"] = orderId
        elif origClientOrderId is not None:
            params["origClientOrderId"] = origClientOrderId
        else:
            return None

        return account.query_order(self.client, symbol, **params)

    def cancel_um_futures_order(self, symbol: str, orderId: Optional[int] = None,
                                origClientOrderId: Optional[str] = None):
        params: Dict[str, Any] = dict()
        if orderId is not None:
            params["orderId"] = orderId
        elif origClientOrderId is not None:
            params["origClientOrderId"] = origClientOrderId
        else:
            return None

        return account.cancel_order(self.client, symbol, **params)

    def get_um_futures_position_risk(self, symbol: Optional[str] = None):
        params: Dict[str, Any] = dict()
        if symbol is not None:
            params["symbol"] = symbol

        return account.get_position_risk(self.client, **params)


if __name__ == "__main__":
    Envs.load_from_env_file("../.env")
    c = UmFuturesClient()
    print(c.get_um_futures_server_timestamp())
    print(c.get_um_futures_exchange_info())
    print(c.get_um_futures_ticker_price("BTCUSDT"))
    print(c.get_um_futures_book_ticker("BTCUSDT"))
    print(c.get_um_futures_balance())
    print(c.get_um_futures_account())
    print(c.get_um_futures_funding_rate("BTCUSDT"))
    print(c.get_um_futures_klines("BTCUSDT", "1m"))
