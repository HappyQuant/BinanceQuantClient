# BinanceQuant

币安量化交易客户端，支持同步和异步两种模式。

## 安装

```bash
pipenv install
```

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

### 同步模式 (原有代码)

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

### 异步模式 (新增)

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
BinanceQuant/
├── envs.py                    # 环境配置
├── utils/
│   ├── redis_client.py        # 同步 Redis 客户端
│   ├── redis_client_async.py  # 异步 Redis 客户端
│   └── async_task_manager.py  # 异步任务管理器
├── spot/
│   ├── api.py                 # 同步现货 REST API
│   ├── api_async.py           # 异步现货 REST API
│   ├── ws.py                  # 同步现货 WebSocket
│   └── ws_async.py            # 异步现货 WebSocket
├── futures/
│   ├── um_api.py              # 同步 U本位 REST API
│   ├── um_api_async.py        # 异步 U本位 REST API
│   ├── um_ws.py               # 同步 U本位 WebSocket
│   ├── um_ws_async.py         # 异步 U本位 WebSocket
│   ├── cm_api.py              # 同步币本位 REST API
│   ├── cm_api_async.py        # 异步币本位 REST API
│   ├── cm_ws.py               # 同步币本位 WebSocket
│   └── cm_ws_async.py         # 异步币本位 WebSocket
└── examples_async.py          # 异步使用示例
```

## 运行示例

```bash
python examples_async.py
```
