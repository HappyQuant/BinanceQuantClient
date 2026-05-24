import asyncio
from binance import BinanceSocketManager, Client

PROXIES = {"http": "http://127.0.0.1:1080", "https": "http://127.0.0.1:1080"}
WS_PROXY = "http://127.0.0.1:1080"
SYMBOL = "BTCUSDT"
WS_TIMEOUT = 20

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
    print("Spot WebSocket API Test")
    print(f"Symbol: {SYMBOL} | Proxy: {WS_PROXY}")
    print("=" * 60)

    client = Client(requests_params={"proxies": PROXIES})
    client.https_proxy = WS_PROXY
    bsm = BinanceSocketManager(client)

    await test_stream("Spot Trade", bsm.trade_socket(SYMBOL))
    await test_stream("Spot AggTrade", bsm.aggtrade_socket(SYMBOL))
    await test_stream("Spot Kline (1m)", bsm.kline_socket(SYMBOL, interval="1m"))
    await test_stream("Spot Depth (5)", bsm.depth_socket(SYMBOL, depth="5"))
    await test_stream("Spot Ticker", bsm.ticker_socket())
    await test_stream("Spot Symbol Ticker", bsm.symbol_ticker_socket(SYMBOL))
    await test_stream("Spot Book Ticker", bsm.symbol_book_ticker_socket(SYMBOL))
    await test_stream("Spot Mini Ticker", bsm.miniticker_socket())

    print("\n" + "=" * 60)
    print(f"SUMMARY: Passed={passed}  Failed={failed}  Total={passed + failed}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
