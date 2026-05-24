from binance import Client

PROXIES = {"http": "http://127.0.0.1:1080", "https": "http://127.0.0.1:1080"}
SYMBOL = "BTCUSDT"

passed = 0
failed = 0


def run_test(name, fn):
    global passed, failed
    try:
        result = fn()
        passed += 1
        print(f"  [OK] {name}: {str(result)[:200]}")
    except Exception as e:
        failed += 1
        print(f"  [FAIL] {name}: {e}")


def main():
    global passed, failed

    print("=" * 60)
    print("Futures REST API — Sync Mode (Client)")
    print(f"Symbol: {SYMBOL} | Proxy: 127.0.0.1:1080")
    print("=" * 60)

    client = Client(requests_params={"proxies": PROXIES})

    tests = [
        ("Futures Ping", lambda: client.futures_ping()),
        ("Futures Server Time", lambda: client.futures_time()),
        ("Futures Exchange Info", lambda: client.futures_exchange_info()),
        ("Futures Order Book", lambda: client.futures_order_book(symbol=SYMBOL, limit=5)),
        ("Futures Recent Trades", lambda: client.futures_recent_trades(symbol=SYMBOL, limit=5)),
        ("Futures Aggregate Trades", lambda: client.futures_aggregate_trades(symbol=SYMBOL, limit=5)),
        ("Futures Klines", lambda: client.futures_klines(symbol=SYMBOL, interval="1m", limit=5)),
        ("Futures Mark Price", lambda: client.futures_mark_price(symbol=SYMBOL)),
        ("Futures Funding Rate", lambda: client.futures_funding_rate(symbol=SYMBOL, limit=5)),
        ("Futures 24h Ticker", lambda: client.futures_ticker(symbol=SYMBOL)),
        ("Futures Symbol Ticker", lambda: client.futures_symbol_ticker(symbol=SYMBOL)),
        ("Futures Orderbook Ticker", lambda: client.futures_orderbook_ticker(symbol=SYMBOL)),
        ("Futures Open Interest", lambda: client.futures_open_interest(symbol=SYMBOL)),
    ]

    for name, fn in tests:
        run_test(name, fn)

    print("\n" + "=" * 60)
    print(f"SUMMARY: Passed={passed}  Failed={failed}  Total={passed + failed}")
    print("=" * 60)


if __name__ == "__main__":
    main()
