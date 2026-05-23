#!/usr/bin/env python
# encoding: utf-8
import json
import threading
import time

from binance.websocket.spot.websocket_stream import SpotWebsocketStreamClient

from envs import Envs
from gvars import GVars
from utils.redis_client import RedisClient


def register_spot_ws_callback(on_message_callback, on_close_callback=None, on_error_callback=None):
    Envs.initialize()
    GVars.initialize()
    return SpotWebsocketStreamClient(
        on_message=on_message_callback,
        on_close=on_close_callback,
        on_error=on_error_callback,
        timeout=Envs.WsClientTimeout,
        proxies=Envs.WsClientProxy,
    )


def spot_ws_partial_book_callback(symbol: str):
    def message_handler(_, message):
        msg_obj = json.loads(message)
        if "bids" in msg_obj and "asks" in msg_obj:
            RedisClient.set("spot_partial_book_{}".format(symbol), message, 3)

    spot_ws_cli = register_spot_ws_callback(on_message_callback=message_handler)
    spot_ws_cli.partial_book_depth(symbol=symbol)

    while not GVars.global_spot_ws_thread_stop:
        time.sleep(1)


def run_spot_ws_partial_book_thread(symbol: str, daemon: bool) -> threading.Thread:
    ws_thread = threading.Thread(target=spot_ws_partial_book_callback, args=(symbol,), daemon=daemon)
    ws_thread.start()
    return ws_thread


if __name__ == "__main__":
    Envs.load_from_env_file("../.env")
    t = run_spot_ws_partial_book_thread(Envs.WsSpotPairs[0], daemon=False)
    t.join()
