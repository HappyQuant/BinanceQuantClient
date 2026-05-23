#!/usr/bin/env python
# encoding: utf-8
import json
import threading
import time

from binance.websocket.cm_futures.websocket_client import CMFuturesWebsocketClient

from envs import Envs
from gvars import GVars
from utils.redis_client import RedisClient


def register_cm_futures_ws_callback(on_message_callback, on_close_callback=None, on_error_callback=None):
    Envs.initialize()
    GVars.initialize()
    return CMFuturesWebsocketClient(
        on_message=on_message_callback,
        on_close=on_close_callback,
        on_error=on_error_callback,
        timeout=Envs.WsClientTimeout,
        proxies=Envs.WsClientProxy,
    )


def cm_futures_ws_partial_book_callback(symbol: str):
    def message_handler(_, message):
        msg_obj = json.loads(message)
        if "b" in msg_obj and "a" in msg_obj:
            RedisClient.set("cm_futures_partial_book_{}".format(symbol), message, 3)

    cm_futures_ws_cli = register_cm_futures_ws_callback(on_message_callback=message_handler)
    cm_futures_ws_cli.partial_book_depth(symbol=symbol)

    while not GVars.global_cm_futures_ws_thread_stop:
        time.sleep(1)


def run_cm_futures_ws_partial_book_thread(symbol: str, daemon: bool) -> threading.Thread:
    ws_thread = threading.Thread(target=cm_futures_ws_partial_book_callback, args=(symbol,), daemon=daemon)
    ws_thread.start()
    return ws_thread


if __name__ == "__main__":
    Envs.load_from_env_file("../.env")
    t = run_cm_futures_ws_partial_book_thread(Envs.WsCmFuturesPairs[0], daemon=False)
    t.join()
