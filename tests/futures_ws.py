import asyncio
from binance import BinanceSocketManager, Client
from binance.enums import FuturesType

PROXIES = {"http": "http://127.0.0.1:1080", "https": "http://127.0.0.1:1080"}
WS_PROXY = "http://127.0.0.1:1080"
USDM_SYMBOL = "BTCUSDT"
COINM_SYMBOL = "BTCUSD_PERP"
WS_TIMEOUT = 15

passed = 0
failed = 0


async def test_stream(name, socket_ctx):
    global passed, failed
    async with socket_ctx as socket:
        try:
            msg = await asyncio.wait_for(socket.recv(), timeout=WS_TIMEOUT)
            passed += 1
            print(f"  [OK] {name}: {str(msg)[:200]}")
        except asyncio.TimeoutError:
            failed += 1
            print(f"  [FAIL] {name}: timeout ({WS_TIMEOUT}s)")
        except Exception as e:
            failed += 1
            print(f"  [FAIL] {name}: {e}")


async def main():
    global passed, failed

    print("=" * 60)
    print("Futures WebSocket API Test")
    print(f"USDM Symbol: {USDM_SYMBOL} | COINM Symbol: {COINM_SYMBOL} | Proxy: {WS_PROXY}")
    print("=" * 60)

    client = Client(requests_params={"proxies": PROXIES})
    client.https_proxy = WS_PROXY
    bsm = BinanceSocketManager(client)

    print("\n--- USDM Futures (FuturesType.USD_M) ---")
    await test_stream("USDM AggTrade", bsm.aggtrade_futures_socket(USDM_SYMBOL))
    await test_stream("USDM Kline (1m)", bsm.kline_futures_socket(USDM_SYMBOL, interval="1m"))
    await test_stream("USDM Mark Price", bsm.symbol_mark_price_socket(USDM_SYMBOL))
    await test_stream("USDM Depth (10)", bsm.futures_depth_socket(USDM_SYMBOL, depth="10"))
    await test_stream("USDM Symbol Ticker", bsm.individual_symbol_ticker_futures_socket(USDM_SYMBOL))
    await test_stream("USDM All Mark Price", bsm.all_mark_price_socket())
    await test_stream("USDM All Book Ticker", bsm.all_ticker_futures_socket())

    print("\n--- COIN-M Futures (FuturesType.COIN_M) ---")
    await test_stream(
        "COIN-M Mark Price",
        bsm.symbol_mark_price_socket(COINM_SYMBOL, futures_type=FuturesType.COIN_M),
    )
    await test_stream(
        "COIN-M Depth (10)",
        bsm.futures_depth_socket(COINM_SYMBOL, depth="10", futures_type=FuturesType.COIN_M),
    )
    await test_stream(
        "COIN-M Symbol Ticker",
        bsm.individual_symbol_ticker_futures_socket(COINM_SYMBOL, futures_type=FuturesType.COIN_M),
    )
    await test_stream(
        "COIN-M Index Price",
        bsm.index_price_socket("BTCUSD", fast=True),
    )
    await test_stream(
        "COIN-M All Ticker",
        bsm.futures_coin_ticker_socket(),
    )
    await test_stream(
        "COIN-M RPI Depth",
        bsm.futures_rpi_depth_socket(COINM_SYMBOL, futures_type=FuturesType.COIN_M),
    )

    print("\n" + "=" * 60)
    print(f"SUMMARY: Passed={passed}  Failed={failed}  Total={passed + failed}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
