# BinanceQuantClient

币安量化交易客户端，支持同步和异步两种模式。

## 特性

- 统一使用 `python-binance` SDK，支持同步和异步
- 支持 Spot 现货交易
- 支持 U本位合约 (UM Futures)
- 支持币本位合约 (CM Futures)
- 支持 REST API 和 WebSocket
- 支持代理配置

## 安装

### 使用 pip (推荐)

```bash
pip install -r requirements.txt
```

### 使用 pipenv

```bash
pipenv install
```

**注意**: 项目已迁移到统一使用 `python-binance` SDK，不再依赖 `binance-connector` 或 `binance-futures-connector`。

## 配置

创建 `.env` 文件：

```
API_KEY=<binance api key>
API_SECRET=<binance api secret>

CLIENT_TIMEOUT=3
CLIENT_SHOW_LIMIT=false
CLIENT_SHOW_HEADER=false
CLIENT_PROXY={"https":"http://127.0.0.1:1080"}

WS_CLIENT_TIMEOUT=5
WS_CLIENT_PROXY={"https":"http://127.0.0.1:1080"}

WS_SPOT_PAIRS=["BTCUSDT"]
WS_CM_FUTURES_PAIRS=[]
WS_UM_FUTURES_PAIRS=["BTCUSDT"]

REDIS_URL="redis://127.0.0.1:6379/20"
```

## 使用

### 同步模式

```python
from spot import SpotClient
from futures import UmFuturesClient, CmFuturesClient
from utils import RedisClient

# 现货
client = SpotClient()
ticker = client.get_spot_ticker_price("BTCUSDT")
print(ticker)

# U本位期货
um_client = UmFuturesClient()
ticker = um_client.get_um_futures_ticker_price("BTCUSDT")
print(ticker)

# 币本位期货
cm_client = CmFuturesClient()
ticker = cm_client.get_cm_futures_ticker_price("BTCUSD_PERP")
print(ticker)
```

### 异步模式

```python
import asyncio
from spot import AsyncSpotClient
from futures import AsyncUmFuturesClient, AsyncCmFuturesClient
from utils import AsyncTaskManager, AsyncRedisClient
from spot.ws_async import AsyncSpotWebSocket

async def main():
    # 异步 REST API
    client = AsyncSpotClient()
    ticker = await client.get_spot_ticker_price("BTCUSDT")
    print(ticker)
    await client.close()

    # 异步 WebSocket
    manager = AsyncTaskManager()
    await manager.start()

    ws = AsyncSpotWebSocket(manager)
    await ws.subscribe_partial_book_depth("BTCUSDT")

    await asyncio.sleep(30)
    await manager.stop()

asyncio.run(main())
```

### 并发请求示例

```python
import asyncio
from spot import AsyncSpotClient

async def get_multiple_prices():
    client = AsyncSpotClient()

    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
    tasks = [client.get_spot_ticker_price(s) for s in symbols]
    results = await asyncio.gather(*tasks)

    for symbol, ticker in zip(symbols, results):
        print(f"{symbol}: {ticker}")

    await client.close()

asyncio.run(get_multiple_prices())
```

## 项目结构

```
BinanceQuantClient/
├── requirements.txt            # 项目依赖
├── envs.py                     # 环境配置
├── gvars.py                    # 全局变量
├── utils/
│   ├── redis_client.py         # 同步 Redis 客户端
│   ├── redis_client_async.py   # 异步 Redis 客户端
│   └── async_task_manager.py   # 异步任务管理器
├── spot/
│   ├── api.py                  # 同步现货 REST API (基于 python-binance Client)
│   ├── api_async.py            # 异步现货 REST API (基于 python-binance AsyncClient)
│   ├── ws.py                   # 同步现货 WebSocket
│   └── ws_async.py             # 异步现货 WebSocket
├── futures/
│   ├── um_api.py               # 同步 U本位 REST API (基于 python-binance Client)
│   ├── um_api_async.py         # 异步 U本位 REST API (基于 python-binance AsyncClient)
│   ├── um_ws.py                # 同步 U本位 WebSocket
│   ├── um_ws_async.py          # 异步 U本位 WebSocket
│   ├── cm_api.py               # 同步币本位 REST API (基于 python-binance Client)
│   ├── cm_api_async.py         # 异步币本位 REST API (基于 python-binance AsyncClient)
│   ├── cm_ws.py                # 同步币本位 WebSocket
│   └── cm_ws_async.py          # 异步币本位 WebSocket
└── examples_async.py           # 异步使用示例
```

## SDK 依赖

本项目统一使用 `python-binance` SDK：

| 功能 | 同步客户端 | 异步客户端 |
|------|-----------|-----------|
| Spot 现货 | `Client` | `AsyncClient` |
| UM U本位合约 | `Client.futures_*` | `AsyncClient.futures_*` |
| CM 币本位合约 | `Client.futures_coin_*` | `AsyncClient.futures_coin_*` |

### 为什么选择 python-binance?

- 社区维护活跃，功能完善
- 同时支持同步和异步操作
- 统一的 API 设计，易于使用
- 支持 Spot、UM Futures、CM Futures 全部交易类型

## 运行示例

```bash
python examples_async.py
```

## 注意事项

1. **代理配置**: 同步客户端和异步客户端的代理配置方式不同
   - 同步: `requests_params={"proxies": {...}}`
   - 异步: `session_params={"proxy": "..."}`

2. **超时配置**: 超时时间在 `requests_params` 中设置，单位为秒

3. **环境变量**: 确保 `.env` 文件正确配置，特别是 API_KEY 和 API_SECRET
