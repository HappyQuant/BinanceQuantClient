#!/usr/bin/env python
# encoding: utf-8


import json
import os
from typing import Optional, Dict, List

from dotenv import load_dotenv


class Envs(object):
    Initialized: bool = False
    ApiKey: str = ""
    ApiSecret: str = ""
    ClientTimeout: int = 0
    ClientShowLimit: bool = False
    ClientShowHeader: bool = False
    ClientProxy: Dict = dict()
    WsClientTimeout: int = 0
    WsClientProxy: Dict = dict()
    WsSpotPairs: List = list()
    WsCmFuturesPairs: List = list()
    WsUmFuturesPairs: List = list()
    RedisUrl: str = ""

    @staticmethod
    def load_from_env_file(env_file: str = ".env"):
        load_dotenv(dotenv_path=env_file)
        Envs.initialize()

    @staticmethod
    def initialize():
        if Envs.Initialized:
            return

        api_key_opt: Optional[str] = os.getenv("API_KEY")
        assert api_key_opt is not None
        Envs.ApiKey = str(api_key_opt)

        api_secret_opt: Optional[str] = os.getenv("API_SECRET")
        assert api_secret_opt is not None
        Envs.ApiSecret = str(api_secret_opt)

        client_timeout_opt: Optional[str] = os.getenv("CLIENT_TIMEOUT")
        assert client_timeout_opt is not None
        Envs.ClientTimeout = int(client_timeout_opt)

        client_show_limit_opt: Optional[str] = os.getenv("CLIENT_SHOW_LIMIT")
        assert client_show_limit_opt is not None
        Envs.ClientShowLimit = False if str(client_show_limit_opt).lower() == "false" else True

        client_show_header_opt: Optional[str] = os.getenv("CLIENT_SHOW_HEADER")
        assert client_show_header_opt is not None
        Envs.ClientShowHeader = False if str(client_show_header_opt).lower() == "false" else True

        client_proxy_opt: Optional[str] = os.getenv("CLIENT_PROXY")
        assert client_proxy_opt is not None
        Envs.ClientProxy = json.loads(str(client_proxy_opt))
        assert isinstance(Envs.ClientProxy, dict)

        ws_client_timeout_opt: Optional[str] = os.getenv("WS_CLIENT_TIMEOUT")
        assert ws_client_timeout_opt is not None
        Envs.WsClientTimeout = int(str(ws_client_timeout_opt))

        ws_client_proxy_opt: Optional[str] = os.getenv("WS_CLIENT_PROXY")
        assert ws_client_proxy_opt is not None
        Envs.WsClientProxy = json.loads(ws_client_proxy_opt)
        assert isinstance(Envs.WsClientProxy, dict)

        ws_spot_pairs_opt: Optional[str] = os.getenv("WS_SPOT_PAIRS")
        assert ws_spot_pairs_opt is not None
        Envs.WsSpotPairs = json.loads(ws_spot_pairs_opt)
        assert isinstance(Envs.WsSpotPairs, list)

        ws_cm_futures_pairs_opt: Optional[str] = os.getenv("WS_CM_FUTURES_PAIRS")
        assert ws_cm_futures_pairs_opt is not None
        Envs.WsCmFuturesPairs = json.loads(ws_cm_futures_pairs_opt)
        assert isinstance(Envs.WsCmFuturesPairs, list)

        ws_um_futures_pairs_opt: Optional[str] = os.getenv("WS_UM_FUTURES_PAIRS")
        assert ws_um_futures_pairs_opt is not None
        Envs.WsUmFuturesPairs = json.loads(ws_um_futures_pairs_opt)
        assert isinstance(Envs.WsUmFuturesPairs, list)

        redis_url_opt: Optional[str] = os.getenv("REDIS_URL")
        assert redis_url_opt is not None
        Envs.RedisUrl = str(redis_url_opt)

        Envs.Initialized = True
