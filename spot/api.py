#!/usr/bin/env python
# encoding: utf-8
import time
from enum import Enum
from typing import Optional, Dict, Any

from binance import Client
from binance import enums

from envs import Envs
from gvars import GVars


class TimeInForceEnum(Enum):
    # Good Til Canceled
    GTC = "GTC"
    # Immediate Or Cancel
    IOC = "IOC"
    # Fill or Kill
    FOK = "FOK"


class SpotClient(object):
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

    def get_spot_server_timestamp(self):
        return self.client.get_server_time()

    def get_spot_exchange_info(self):
        return self.client.get_exchange_info()

    def get_spot_trade_fee(self):
        return self.client.get_trade_fee()

    def get_spot_ticker_price(self, symbol: str):
        return self.client.get_symbol_ticker(symbol=symbol)

    def get_spot_balance(self):
        return self.client.get_account()

    def get_spot_account(self):
        return self.client.get_account()

    def get_spot_klines(self, symbol: str, interval: str, limit: int = 50, end_time: int = int(time.time() * 1000)):
        return self.client.get_klines(
            symbol=symbol,
            interval=interval,
            limit=limit,
            endTime=end_time
        )

    def place_limit_order(self, symbol: str, side: str, price: float, quantity: Optional[float] = None,
                          quoteOrderQty: Optional[float] = None, timeInForce: TimeInForceEnum = TimeInForceEnum.GTC,
                          newClientOrderId: Optional[str] = None):
        params: Dict[str, Any] = {
            "type": enums.ORDER_TYPE_LIMIT,
            "price": price,
            "timeInForce": timeInForce.value,
        }
        if quantity is not None:
            params["quantity"] = quantity
        elif quoteOrderQty is not None:
            params["quoteOrderQty"] = quoteOrderQty
        else:
            return None

        if newClientOrderId is not None:
            params["newClientOrderId"] = newClientOrderId
        return self.client.create_order(
            symbol=symbol,
            side=side,
            **params
        )

    def place_market_order(self, symbol: str, side: str, quantity: Optional[float] = None,
                           quoteOrderQty: Optional[float] = None,
                           newClientOrderId: Optional[str] = None):
        params: Dict[str, Any] = {
            "type": enums.ORDER_TYPE_MARKET,
        }
        if quantity is not None:
            params["quantity"] = quantity
        elif quoteOrderQty is not None:
            params["quoteOrderQty"] = quoteOrderQty
        else:
            return None

        if newClientOrderId is not None:
            params["newClientOrderId"] = newClientOrderId
        return self.client.create_order(
            symbol=symbol,
            side=side,
            **params
        )

    def get_order(self, symbol: str, orderId: Optional[int] = None, origClientOrderId: Optional[str] = None):
        params: Dict[str, Any] = {"symbol": symbol}
        if orderId is not None:
            params["orderId"] = orderId
        elif origClientOrderId is not None:
            params["origClientOrderId"] = origClientOrderId
        else:
            return None

        return self.client.get_order(**params)

    def cancel_order(self, symbol: str, orderId: Optional[int] = None, origClientOrderId: Optional[str] = None):
        params: Dict[str, Any] = {"symbol": symbol}
        if orderId is not None:
            params["orderId"] = orderId
        elif origClientOrderId is not None:
            params["origClientOrderId"] = origClientOrderId
        else:
            return None

        return self.client.cancel_order(**params)


if __name__ == "__main__":
    Envs.load_from_env_file("../.env")
    c = SpotClient()
    print(c.get_spot_server_timestamp())
    print(c.get_spot_exchange_info())
    print(c.get_spot_trade_fee())
    print(c.get_spot_ticker_price("BTCUSDT"))
    print(c.get_spot_balance())
    print(c.get_spot_account())
    print(c.get_spot_klines("BTCUSDT", "1s"))
    print(c.place_limit_order("DYDXFDUSD", "BUY", quantity=5.0, price=1.0, timeInForce=TimeInForceEnum.GTC,
                              newClientOrderId="idXjNcAB7RGdj3t1qnylp5"))
    print(c.get_order("DYDXFDUSD", origClientOrderId="idXjNcAB7RGdj3t1qnylp5"))
    print(c.cancel_order("DYDXFDUSD", origClientOrderId="idXjNcAB7RGdj3t1qnylp5"))
