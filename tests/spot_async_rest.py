import asyncio
from binance import AsyncClient

PROXIES = {"http": "http://127.0.0.1:1080", "https": "http://127.0.0.1:1080"}
SYMBOL = "BTCUSDT"

passed = 0
failed = 0


async def run_test(name, fn):
    global passed, failed
    try:
        result = await fn()
        passed += 1
        print(f"  [OK] {name}: {str(result)[:200]}")
    except Exception as e:
        failed += 1
        print(f"  [FAIL] {name}: {e}")


async def main():
    global passed, failed

    print("=" * 60)
    print("Spot REST API — Async Mode (AsyncClient)")
    print(f"Symbol: {SYMBOL} | Proxy: 127.0.0.1:1080")
    print("=" * 60)

    client = await AsyncClient().create(
        requests_params={"proxies": PROXIES},
        https_proxy="http://127.0.0.1:1080",
    )

    try:
        tests = [
            ("Server Time", lambda: client.get_server_time()),
            ("Order Book", lambda: client.get_order_book(symbol=SYMBOL, limit=5)),
            ("Recent Trades", lambda: client.get_recent_trades(symbol=SYMBOL, limit=5)),
            ("Aggregate Trades", lambda: client.get_aggregate_trades(symbol=SYMBOL, limit=5)),
            ("Klines", lambda: client.get_klines(symbol=SYMBOL, interval="1m", limit=5)),
            ("Avg Price", lambda: client.get_avg_price(symbol=SYMBOL)),
            ("Symbol Ticker", lambda: client.get_symbol_ticker(symbol=SYMBOL)),
            ("24h Ticker", lambda: client.get_ticker(symbol=SYMBOL)),
            ("Orderbook Ticker", lambda: client.get_orderbook_ticker(symbol=SYMBOL)),
            ("Symbol Info", lambda: client.get_symbol_info(SYMBOL)),
        ]

        for name, fn in tests:
            await run_test(name, fn)
    finally:
        await client.close_connection()

    print("\n" + "=" * 60)
    print(f"SUMMARY: Passed={passed}  Failed={failed}  Total={passed + failed}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
