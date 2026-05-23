#!/usr/bin/env python
# encoding: utf-8

from envs import Envs
from utils.redis_client import RedisClient


class GVars(object):
    Initialized: bool = False
    global_spot_ws_thread_stop: bool = False
    global_cm_futures_ws_thread_stop: bool = False
    global_um_futures_ws_thread_stop: bool = False

    @staticmethod
    def initialize():
        if GVars.Initialized:
            return

        GVars.global_spot_ws_thread_stop = False
        GVars.global_cm_futures_ws_thread_stop = False
        GVars.global_um_futures_ws_thread_stop = False
        RedisClient.connect(Envs.RedisUrl)

        GVars.Initialized = True

    @staticmethod
    def stop_all_threads():
        GVars.global_spot_ws_thread_stop = True
        GVars.global_cm_futures_ws_thread_stop = True
        GVars.global_um_futures_ws_thread_stop = True
